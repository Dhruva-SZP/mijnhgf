import pytest
from app.forecast_service import ForecastSelectionService
from app.pipeline import DataPipeline

def test_duplicate_record_handling():
    """Verifies that duplicate actuals for the same settlement interval are deduplicated cleanly."""
    service = ForecastSelectionService(cutoff_hour=11)

    actuals = [
        {"startTime": "2026-01-01T00:00:00Z", "generation": 10000, "fuelType": "WIND", "publishTime": "2026-01-01T00:30:00Z"},
        # Duplicate with same startTime
        {"startTime": "2026-01-01T00:00:00Z", "generation": 10000, "fuelType": "WIND", "publishTime": "2026-01-01T00:25:00Z"}
    ]

    forecasts = [
        {"publishTime": "2025-12-31T09:30:00Z", "startTime": "2026-01-01T00:00:00Z", "generation": 9800}
    ]

    matched_df, meta = service.process_and_match(actuals, forecasts, start_date="2026-01-01", end_date="2026-01-01")

    # Should only produce 1 matched record despite duplicate input
    assert len(matched_df) == 1
    assert matched_df.iloc[0]["startTime"] == "2026-01-01T00:00:00Z"

def test_missing_intervals_calculation():
    """Verifies expected intervals vs matched intervals computation."""
    service = ForecastSelectionService(cutoff_hour=11)

    # 1 day in January = 48 settlement intervals expected
    # Provide only 2 actual intervals
    actuals = [
        {"startTime": "2026-01-01T00:00:00Z", "generation": 10000, "fuelType": "WIND"},
        {"startTime": "2026-01-01T00:30:00Z", "generation": 10200, "fuelType": "WIND"}
    ]
    forecasts = [
        {"publishTime": "2025-12-31T09:30:00Z", "startTime": "2026-01-01T00:00:00Z", "generation": 9800}
    ]

    matched_df, meta = service.process_and_match(actuals, forecasts, start_date="2026-01-01", end_date="2026-01-01")

    assert meta["total_expected_intervals"] == 48
    assert meta["matched_intervals"] == 2
    assert meta["missing_intervals"] == 46
    assert meta["coverage_pct"] == round(2 / 48 * 100, 2)
