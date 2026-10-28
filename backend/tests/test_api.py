import pytest
from app.routes import (
    get_health,
    get_summary,
    get_timeseries,
    get_accuracy,
    get_publication_history,
    get_records,
    get_data_status,
    export_csv
)

def test_health_endpoint():
    data = get_health()
    assert data["status"] == "healthy"
    assert data["service"] == "gridbricks-wind-procurement-backend"

def test_summary_endpoint():
    data = get_summary(start="2026-01-01", end="2026-01-05", cutoff=11)
    assert data["total_actual_generation_mwh"] > 0
    assert data["avg_actual_generation_mw"] > 0
    assert data["mae_mw"] > 0
    assert data["rmse_mw"] > 0
    assert data["wape_pct"] > 0
    assert data["coverage_pct"] > 90.0
    assert data["matched_intervals"] > 0
    assert data["day_ahead_cutoff_hour"] == 11

def test_timeseries_endpoint():
    data = get_timeseries(start="2026-01-01", end="2026-01-02", cutoff=11)
    assert "points" in data
    assert "metadata" in data
    points = data["points"]
    assert len(points) == 96  # 2 days * 48 half-hours
    first = points[0]
    assert first["startTime"] == "2026-01-01T00:00:00Z"
    assert "actual_mw" in first
    assert "forecast_mw" in first
    assert "signed_error_mw" in first
    assert "abs_error_mw" in first
    assert first["publishTime"] is not None

def test_accuracy_endpoint():
    data = get_accuracy(start="2026-01-01", end="2026-01-05", cutoff=11)
    assert data["overall_kpis"]["matched_intervals"] > 0
    assert len(data["daily_metrics"]) == 5  # Jan 1 to Jan 5
    assert len(data["hourly_profile"]) == 24
    assert len(data["error_distribution"]) > 0
    assert len(data["largest_errors"]) > 0
    assert "Over-forecast" in data["largest_errors"][0]["implication"] or "Under-forecast" in data["largest_errors"][0]["implication"]

def test_publication_history_endpoint():
    data = get_publication_history(start="2026-01-01", end="2026-01-05", cutoff=11)
    assert data["decision_cutoff_hour"] == 11
    assert len(data["versions"]) > 0
    assert data["total_matched"] > 0
    assert data["leakage_prevented_count"] > 0

def test_records_endpoint_pagination():
    data = get_records(start="2026-01-01", end="2026-01-05", cutoff=11, page=1, page_size=20)
    assert data["page"] == 1
    assert data["page_size"] == 20
    assert len(data["records"]) == 20
    assert data["total_records"] == 5 * 48  # 240 intervals
    assert data["total_pages"] == 12

def test_data_status_endpoint():
    data = get_data_status()
    assert data["actual_records_count"] > 0
    assert data["forecast_records_count"] > 0
    assert data["matched_intervals_count"] > 0
    assert "Elexon" in data["message"]

def test_export_csv_endpoint():
    response = export_csv(start="2026-01-01", end="2026-01-02", cutoff=11)
    assert response.media_type == "text/csv"
    assert "attachment" in response.headers["Content-Disposition"]
