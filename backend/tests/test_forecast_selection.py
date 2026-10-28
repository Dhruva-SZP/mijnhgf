import pytest
import pandas as pd
from app.forecast_service import ForecastSelectionService

def test_forecast_selection_at_day_ahead_cutoff():
    """
    Verifies that for delivery on 2026-01-02, the forecast selected is the latest
    forecast published on or before 11:00 UTC on 2026-01-01.
    """
    service = ForecastSelectionService(cutoff_hour=11)

    # Actual delivery at 14:00 on 2026-01-02
    actuals = [
        {
            "startTime": "2026-01-02T14:00:00Z",
            "generation": 10000,
            "fuelType": "WIND",
            "settlementDate": "2026-01-02",
            "settlementPeriod": 29
        }
    ]

    # Forecasts published at different times
    forecasts = [
        # Published D-1 at 04:30 (Eligible, but early)
        {"publishTime": "2026-01-01T04:30:00Z", "startTime": "2026-01-02T14:00:00Z", "generation": 8000},
        # Published D-1 at 09:30 (Eligible, latest before 11:00 cutoff -> MUST BE SELECTED)
        {"publishTime": "2026-01-01T09:30:00Z", "startTime": "2026-01-02T14:00:00Z", "generation": 9500},
        # Published D-1 at 11:30 (After 11:00 cutoff -> FUTURE LEAKAGE, MUST BE EXCLUDED)
        {"publishTime": "2026-01-01T11:30:00Z", "startTime": "2026-01-02T14:00:00Z", "generation": 10500},
        # Published D at 02:30 (Intraday -> MUST BE EXCLUDED)
        {"publishTime": "2026-01-02T02:30:00Z", "startTime": "2026-01-02T14:00:00Z", "generation": 9900}
    ]

    matched_df, meta = service.process_and_match(actuals, forecasts, start_date="2026-01-02", end_date="2026-01-02", cutoff_hour=11)

    assert len(matched_df) == 1
    row = matched_df.iloc[0]
    
    # Assert the 09:30 run was selected
    assert row["publishTime"] == "2026-01-01T09:30:00Z"
    assert row["forecast_mw"] == 9500
    assert row["actual_mw"] == 10000
    assert row["signed_error_mw"] == -500  # 9500 - 10000
    assert row["abs_error_mw"] == 500

    # Leakage prevented count should include the two post-cutoff forecasts
    assert meta["leakage_prevented_count"] == 2

def test_future_data_leakage_prevention():
    """
    Ensures that if all available forecasts were published AFTER the cutoff,
    none are selected to prevent contaminated future data from entering day-ahead analysis.
    """
    service = ForecastSelectionService(cutoff_hour=11)

    actuals = [
        {
            "startTime": "2026-01-05T10:00:00Z",
            "generation": 12000,
            "fuelType": "WIND",
            "settlementDate": "2026-01-05",
            "settlementPeriod": 21
        }
    ]

    # Only forecasts published AFTER 11:00 UTC on 2026-01-04
    forecasts = [
        {"publishTime": "2026-01-04T15:30:00Z", "startTime": "2026-01-05T10:00:00Z", "generation": 13000},
        {"publishTime": "2026-01-05T06:00:00Z", "startTime": "2026-01-05T10:00:00Z", "generation": 12500}
    ]

    matched_df, meta = service.process_and_match(actuals, forecasts, start_date="2026-01-05", end_date="2026-01-05", cutoff_hour=11)

    # Should not match because no valid day-ahead forecast existed prior to cutoff
    assert len(matched_df) == 0
    assert meta["matched_intervals"] == 0
    assert meta["leakage_prevented_count"] == 2

def test_settlement_period_hourly_mapping():
    """
    Ensures both 30-minute settlement periods in an hour (e.g. 10:00 and 10:30)
    map appropriately to the hourly WINDFOR forecast for 10:00.
    """
    service = ForecastSelectionService(cutoff_hour=11)

    actuals = [
        {"startTime": "2026-01-10T10:00:00Z", "generation": 14000, "fuelType": "WIND", "settlementDate": "2026-01-10", "settlementPeriod": 21},
        {"startTime": "2026-01-10T10:30:00Z", "generation": 14500, "fuelType": "WIND", "settlementDate": "2026-01-10", "settlementPeriod": 22}
    ]

    forecasts = [
        {"publishTime": "2026-01-09T09:30:00Z", "startTime": "2026-01-10T10:00:00Z", "generation": 14200}
    ]

    matched_df, meta = service.process_and_match(actuals, forecasts, start_date="2026-01-10", end_date="2026-01-10", cutoff_hour=11)

    assert len(matched_df) == 2
    assert matched_df.iloc[0]["forecast_mw"] == 14200
    assert matched_df.iloc[1]["forecast_mw"] == 14200
    assert matched_df.iloc[0]["actual_mw"] == 14000
    assert matched_df.iloc[1]["actual_mw"] == 14500
