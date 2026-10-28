import pytest
import numpy as np
import pandas as pd
from app.metrics import MetricsCalculator

def test_accuracy_metrics_known_values():
    """Tests accuracy metrics against precisely calculated known values."""
    # Data:
    # Actual:   [1000, 2000, 3000, 4000]
    # Forecast: [1200, 1800, 3500, 3500]
    # Errors:   [ +200,  -200,  +500,  -500]
    # |Errors|: [  200,   200,   500,   500]
    # Sum Actual = 10,000 MW
    # Mean |Error| (MAE) = 1400 / 4 = 350 MW
    # Error^2 = [40000, 40000, 250000, 250000] = 580,000 -> Mean = 145,000 -> RMSE = sqrt(145000) = 380.78865...
    # Mean Error (Bias) = 0 MW
    # WAPE = 1400 / 10000 * 100% = 14.0%
    # Actual MWh = 10000 * 0.5 = 5000 MWh
    # Total Abs Error MWh = 1400 * 0.5 = 700 MWh

    df = pd.DataFrame({
        "actual_mw": [1000.0, 2000.0, 3000.0, 4000.0],
        "forecast_mw": [1200.0, 1800.0, 3500.0, 3500.0]
    })
    meta = {
        "total_expected_intervals": 4,
        "matched_intervals": 4,
        "missing_intervals": 0,
        "coverage_pct": 100.0,
        "cutoff_hour": 11
    }

    kpis = MetricsCalculator.calculate_summary_kpis(df, meta)

    assert kpis["mae_mw"] == 350.0
    assert pytest.approx(kpis["rmse_mw"], 0.1) == 380.8
    assert kpis["bias_mw"] == 0.0
    assert kpis["wape_pct"] == 14.0
    assert kpis["total_actual_generation_mwh"] == 5000.0
    assert kpis["total_absolute_error_mwh"] == 700.0
    assert kpis["matched_intervals"] == 4

def test_safe_division_on_zero_generation():
    """Ensures WAPE does not raise ZeroDivisionError when actual generation sum is 0."""
    df = pd.DataFrame({
        "actual_mw": [0.0, 0.0],
        "forecast_mw": [50.0, 100.0]
    })
    meta = {
        "total_expected_intervals": 2,
        "matched_intervals": 2,
        "missing_intervals": 0,
        "coverage_pct": 100.0,
        "cutoff_hour": 11
    }

    kpis = MetricsCalculator.calculate_summary_kpis(df, meta)
    assert kpis["wape_pct"] == 0.0
    assert kpis["mae_mw"] == 75.0

def test_empty_dataframe_metrics():
    """Ensures empty dataframe returns valid default metrics without crashing."""
    df = pd.DataFrame()
    meta = {"total_expected_intervals": 48, "cutoff_hour": 11}
    kpis = MetricsCalculator.calculate_summary_kpis(df, meta)
    assert kpis["matched_intervals"] == 0
    assert kpis["mae_mw"] == 0.0
    assert kpis["rmse_mw"] == 0.0
