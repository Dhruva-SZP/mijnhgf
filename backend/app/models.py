from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class SummaryKPIs(BaseModel):
    total_actual_generation_mwh: float = Field(..., description="Total actual generation in MWh (half-hour MW * 0.5h)")
    total_forecast_generation_mwh: float = Field(..., description="Total forecast generation in MWh")
    avg_actual_generation_mw: float = Field(..., description="Average actual generation in MW")
    avg_forecast_generation_mw: float = Field(..., description="Average forecast generation in MW")
    mae_mw: float = Field(..., description="Mean Absolute Error in MW")
    rmse_mw: float = Field(..., description="Root Mean Squared Error in MW")
    bias_mw: float = Field(..., description="Mean Signed Error / Bias in MW (Forecast - Actual)")
    wape_pct: float = Field(..., description="Weighted Absolute Percentage Error (%)")
    total_absolute_error_mwh: float = Field(..., description="Total Absolute Error in MWh")
    total_intervals: int = Field(..., description="Total expected 30-min settlement intervals")
    matched_intervals: int = Field(..., description="Number of successfully matched intervals")
    missing_intervals: int = Field(..., description="Number of missing or unmatched intervals")
    coverage_pct: float = Field(..., description="Data coverage percentage")
    day_ahead_cutoff_hour: int = Field(..., description="Hour of D-1 cutoff in UTC (e.g. 11 for 11:00 UTC)")

class TimeseriesPoint(BaseModel):
    startTime: str = Field(..., description="Delivery start timestamp in UTC ISO format")
    settlementDate: str = Field(..., description="Settlement date (YYYY-MM-DD)")
    settlementPeriod: Optional[int] = Field(None, description="UK Settlement period 1-48")
    actual_mw: Optional[float] = Field(None, description="Actual wind generation in MW")
    forecast_mw: Optional[float] = Field(None, description="Day-ahead forecast wind generation in MW")
    signed_error_mw: Optional[float] = Field(None, description="Forecast - Actual in MW")
    abs_error_mw: Optional[float] = Field(None, description="Absolute error in MW")
    publishTime: Optional[str] = Field(None, description="Timestamp when the selected forecast was published")
    cutoffTime: Optional[str] = Field(None, description="Cutoff timestamp applied on D-1")

class DailyAccuracyMetric(BaseModel):
    date: str
    actual_mwh: float
    forecast_mwh: float
    mae_mw: float
    rmse_mw: float
    bias_mw: float
    wape_pct: float
    interval_count: int

class HourlyErrorProfile(BaseModel):
    hour: int
    avg_actual_mw: float
    avg_forecast_mw: float
    mae_mw: float
    bias_mw: float

class ErrorDistributionBin(BaseModel):
    bin_range: str
    bin_start: float
    bin_end: float
    count: int

class LargestErrorItem(BaseModel):
    startTime: str
    settlementPeriod: Optional[int]
    actual_mw: float
    forecast_mw: float
    signed_error_mw: float
    abs_error_mw: float
    publishTime: str
    implication: str

class AccuracyResponse(BaseModel):
    overall_kpis: SummaryKPIs
    daily_metrics: List[DailyAccuracyMetric]
    hourly_profile: List[HourlyErrorProfile]
    error_distribution: List[ErrorDistributionBin]
    largest_errors: List[LargestErrorItem]

class RecordItem(BaseModel):
    id: int
    startTime: str
    settlementDate: str
    settlementPeriod: Optional[int]
    actual_mw: float
    forecast_mw: float
    signed_error_mw: float
    abs_error_mw: float
    publishTime: str
    cutoffTime: str

class RecordsResponse(BaseModel):
    total_records: int
    page: int
    page_size: int
    total_pages: int
    records: List[RecordItem]

class ForecastPublicationVersion(BaseModel):
    publishTime: str
    count: int
    percentage: float
    description: str

class PublicationHistoryResponse(BaseModel):
    decision_cutoff_hour: int
    cutoff_description: str
    total_matched: int
    versions: List[ForecastPublicationVersion]
    leakage_prevented_count: int
    methodology_notes: List[str]

class DataStatusResponse(BaseModel):
    api_connection_status: str
    last_refresh_timestamp: Optional[str]
    is_cached: bool
    actual_records_count: int
    forecast_records_count: int
    matched_intervals_count: int
    missing_intervals_count: int
    period: str
    elexon_live_accessible: bool
    message: str
