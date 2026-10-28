import io
import csv
from typing import Optional
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import StreamingResponse

from app.pipeline import pipeline_instance
from app.models import (
    SummaryKPIs,
    AccuracyResponse,
    RecordsResponse,
    DataStatusResponse,
    PublicationHistoryResponse
)
from app.config import DEFAULT_START_DATE, DEFAULT_END_DATE, DEFAULT_CUTOFF_HOUR

router = APIRouter(prefix="/api", tags=["Gridbricks Energy Procurement API"])

@router.get("/health")
def get_health():
    """Health check endpoint for Docker and monitoring."""
    return {"status": "healthy", "service": "gridbricks-wind-procurement-backend", "version": "1.0.0"}

@router.get("/summary", response_model=SummaryKPIs)
def get_summary(
    start: str = Query(DEFAULT_START_DATE, description="Start date (YYYY-MM-DD)"),
    end: str = Query(DEFAULT_END_DATE, description="End date (YYYY-MM-DD)"),
    cutoff: int = Query(DEFAULT_CUTOFF_HOUR, description="Day-ahead cutoff hour on D-1 (e.g. 11 for 11:00 UTC)")
):
    """
    Executive overview summary KPIs:
    Total actual generation MWh, Average forecast MW, MAE, RMSE, Bias, WAPE,
    Total absolute error, and coverage indicators.
    """
    try:
        return pipeline_instance.get_summary(start_date=start, end_date=end, cutoff_hour=cutoff)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate summary KPIs: {str(e)}")

@router.get("/timeseries")
def get_timeseries(
    start: str = Query(DEFAULT_START_DATE, description="Start date (YYYY-MM-DD)"),
    end: str = Query(DEFAULT_END_DATE, description="End date (YYYY-MM-DD)"),
    cutoff: int = Query(DEFAULT_CUTOFF_HOUR, description="Day-ahead cutoff hour on D-1 (e.g. 11 for 11:00 UTC)")
):
    """
    Time-series dataset for charting actual vs forecast wind generation at 30-min settlement intervals.
    Includes errors and publication timestamps for interactive tooltips.
    """
    try:
        return pipeline_instance.get_timeseries(start_date=start, end_date=end, cutoff_hour=cutoff)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate timeseries data: {str(e)}")

@router.get("/accuracy", response_model=AccuracyResponse)
def get_accuracy(
    start: str = Query(DEFAULT_START_DATE, description="Start date (YYYY-MM-DD)"),
    end: str = Query(DEFAULT_END_DATE, description="End date (YYYY-MM-DD)"),
    cutoff: int = Query(DEFAULT_CUTOFF_HOUR, description="Day-ahead cutoff hour on D-1 (e.g. 11 for 11:00 UTC)")
):
    """
    Comprehensive forecast accuracy breakdown:
    Overall KPIs, Daily breakdown, 24-hour diurnal error profile, Error distribution bins,
    and Top 10 largest forecast error intervals with business implications.
    """
    try:
        return pipeline_instance.get_accuracy(start_date=start, end_date=end, cutoff_hour=cutoff)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to compute accuracy metrics: {str(e)}")

@router.get("/publication-history", response_model=PublicationHistoryResponse)
def get_publication_history(
    start: str = Query(DEFAULT_START_DATE, description="Start date (YYYY-MM-DD)"),
    end: str = Query(DEFAULT_END_DATE, description="End date (YYYY-MM-DD)"),
    cutoff: int = Query(DEFAULT_CUTOFF_HOUR, description="Day-ahead cutoff hour on D-1 (e.g. 11 for 11:00 UTC)")
):
    """
    Forecast publication audit trail:
    Shows which publication run was selected for day-ahead decisions and details future data leakage prevention.
    """
    try:
        return pipeline_instance.get_publication_history(start_date=start, end_date=end, cutoff_hour=cutoff)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch publication history: {str(e)}")

@router.get("/records", response_model=RecordsResponse)
def get_records(
    start: str = Query(DEFAULT_START_DATE, description="Start date (YYYY-MM-DD)"),
    end: str = Query(DEFAULT_END_DATE, description="End date (YYYY-MM-DD)"),
    cutoff: int = Query(DEFAULT_CUTOFF_HOUR, description="Day-ahead cutoff hour on D-1 (e.g. 11 for 11:00 UTC)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=500, description="Items per page"),
    sort_by: str = Query("startTime", description="Field to sort by"),
    sort_desc: bool = Query(False, description="Sort descending if true"),
    search: Optional[str] = Query(None, description="Search term across timestamp fields")
):
    """
    Detailed, paginated, searchable settlement period records table.
    """
    try:
        search_val = search if isinstance(search, str) else None
        sort_by_val = sort_by if isinstance(sort_by, str) else "startTime"
        sort_desc_val = sort_desc if isinstance(sort_desc, bool) else False
        return pipeline_instance.get_records(
            start_date=start,
            end_date=end,
            cutoff_hour=cutoff,
            page=page,
            page_size=page_size,
            sort_by=sort_by_val,
            sort_desc=sort_desc_val,
            search=search_val
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve records: {str(e)}")

@router.get("/data-status", response_model=DataStatusResponse)
def get_data_status():
    """
    Data reliability and cache status:
    Reports Elexon API connection status, cache indicators, record counts, and coverage.
    """
    try:
        return pipeline_instance.get_data_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch data status: {str(e)}")

@router.post("/refresh")
def refresh_data(
    start: str = Query(DEFAULT_START_DATE, description="Start date (YYYY-MM-DD)"),
    end: str = Query(DEFAULT_END_DATE, description="End date (YYYY-MM-DD)")
):
    """
    Triggers an on-demand re-fetch of live datasets from Elexon and updates local cache.
    """
    try:
        pipeline_instance.get_processed_data(start_date=start, end_date=end, force_refresh=True)
        return {"status": "success", "message": "Successfully refreshed live data from Elexon BMRS API and updated local cache."}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to refresh from Elexon API: {str(e)}")

@router.get("/export/csv")
def export_csv(
    start: str = Query(DEFAULT_START_DATE, description="Start date (YYYY-MM-DD)"),
    end: str = Query(DEFAULT_END_DATE, description="End date (YYYY-MM-DD)"),
    cutoff: int = Query(DEFAULT_CUTOFF_HOUR, description="Day-ahead cutoff hour on D-1")
):
    """
    Exports matched actual vs forecast dataset as a downloadable CSV.
    """
    df, _, _ = pipeline_instance.get_processed_data(start_date=start, end_date=end, cutoff_hour=cutoff)
    if df.empty:
        raise HTTPException(status_code=404, detail="No data available for the specified range.")

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "delivery_start_utc", "settlement_date", "settlement_period",
        "actual_mw", "day_ahead_forecast_mw", "signed_error_mw", "abs_error_mw",
        "forecast_publish_time_utc", "decision_cutoff_utc"
    ])
    for _, row in df.iterrows():
        writer.writerow([
            row["startTime"],
            row["settlementDate"],
            row.get("settlementPeriod", ""),
            row["actual_mw"],
            row["forecast_mw"],
            row["signed_error_mw"],
            row["abs_error_mw"],
            row["publishTime"],
            row["cutoffTime"]
        ])
    output.seek(0)
    filename = f"gridbricks_wind_procurement_{start}_to_{end}_cutoff{cutoff}h.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
