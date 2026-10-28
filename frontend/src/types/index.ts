export interface SummaryKPIs {
  total_actual_generation_mwh: number;
  total_forecast_generation_mwh: number;
  avg_actual_generation_mw: number;
  avg_forecast_generation_mw: number;
  mae_mw: number;
  rmse_mw: number;
  bias_mw: number;
  wape_pct: number;
  total_absolute_error_mwh: number;
  total_intervals: number;
  matched_intervals: number;
  missing_intervals: number;
  coverage_pct: number;
  day_ahead_cutoff_hour: number;
}

export interface TimeseriesPoint {
  startTime: string;
  settlementDate: string;
  settlementPeriod?: number;
  actual_mw: number;
  forecast_mw: number;
  signed_error_mw: number;
  abs_error_mw: number;
  publishTime: string;
  cutoffTime: string;
}

export interface TimeseriesResponse {
  points: TimeseriesPoint[];
  metadata: {
    total_expected_intervals: number;
    matched_intervals: number;
    missing_intervals: number;
    coverage_pct: number;
    cutoff_hour: number;
    cutoff_rule: string;
    settlement_resolution: string;
    is_cached: boolean;
  };
  is_cached: boolean;
}

export interface DailyAccuracyMetric {
  date: string;
  actual_mwh: number;
  forecast_mwh: number;
  mae_mw: number;
  rmse_mw: number;
  bias_mw: number;
  wape_pct: number;
  interval_count: number;
}

export interface HourlyErrorProfile {
  hour: number;
  avg_actual_mw: number;
  avg_forecast_mw: number;
  mae_mw: number;
  bias_mw: number;
}

export interface ErrorDistributionBin {
  bin_range: string;
  bin_start: number;
  bin_end: number;
  count: number;
}

export interface LargestErrorItem {
  startTime: string;
  settlementPeriod?: number;
  actual_mw: number;
  forecast_mw: number;
  signed_error_mw: number;
  abs_error_mw: number;
  publishTime: string;
  implication: string;
}

export interface AccuracyResponse {
  overall_kpis: SummaryKPIs;
  daily_metrics: DailyAccuracyMetric[];
  hourly_profile: HourlyErrorProfile[];
  error_distribution: ErrorDistributionBin[];
  largest_errors: LargestErrorItem[];
}

export interface RecordItem {
  id: number;
  startTime: string;
  settlementDate: string;
  settlementPeriod?: number;
  actual_mw: number;
  forecast_mw: number;
  signed_error_mw: number;
  abs_error_mw: number;
  publishTime: string;
  cutoffTime: string;
}

export interface RecordsResponse {
  total_records: number;
  page: number;
  page_size: number;
  total_pages: number;
  records: RecordItem[];
}

export interface ForecastPublicationVersion {
  publishTime: string;
  count: number;
  percentage: number;
  description: string;
}

export interface PublicationHistoryResponse {
  decision_cutoff_hour: number;
  cutoff_description: string;
  total_matched: number;
  versions: ForecastPublicationVersion[];
  leakage_prevented_count: number;
  methodology_notes: string[];
}

export interface DataStatusResponse {
  api_connection_status: string;
  last_refresh_timestamp: string | null;
  is_cached: boolean;
  actual_records_count: number;
  forecast_records_count: number;
  matched_intervals_count: number;
  missing_intervals_count: number;
  period: string;
  elexon_live_accessible: boolean;
  message: string;
}
