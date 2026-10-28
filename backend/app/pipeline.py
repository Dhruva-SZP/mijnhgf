import logging
from typing import Dict, Any, Optional, Tuple
import pandas as pd

from app.elexon_client import ElexonClient
from app.forecast_service import ForecastSelectionService
from app.metrics import MetricsCalculator

logger = logging.getLogger(__name__)

class DataPipeline:
    """Orchestrates data ingestion, caching, forecast matching, and analytics calculation."""

    def __init__(self):
        self.client = ElexonClient()
        self.forecast_service = ForecastSelectionService()
        self._memory_cache = {}

    def get_processed_data(
        self,
        start_date: str = "2026-01-01",
        end_date: str = "2026-01-31",
        cutoff_hour: int = 11,
        force_refresh: bool = False
    ) -> Tuple[pd.DataFrame, Dict[str, Any], bool]:
        """
        Retrieves raw data, matches records, and returns (dataframe, metadata, is_cached).
        Utilizes in-memory caching when parameters match to provide lightning-fast API responses.
        """
        cache_key = f"{start_date}_{end_date}_{cutoff_hour}"
        if not force_refresh and cache_key in self._memory_cache:
            df, meta, is_cached = self._memory_cache[cache_key]
            return df.copy(), meta.copy(), is_cached

        # 1. Fetch raw data from client (live or disk cache)
        actual_records, act_cached = self.client.fetch_actuals(start_date, end_date, force_refresh)
        forecast_records, fc_cached = self.client.fetch_forecasts(start_date, end_date, force_refresh)
        is_cached = act_cached and fc_cached

        # 2. Run forecast matching and cutoff logic
        matched_df, meta = self.forecast_service.process_and_match(
            actual_records=actual_records,
            forecast_records=forecast_records,
            start_date=start_date,
            end_date=end_date,
            cutoff_hour=cutoff_hour
        )

        meta["is_cached"] = is_cached
        meta["raw_actuals_count"] = len(actual_records)
        meta["raw_forecasts_count"] = len(forecast_records)

        # Store in memory cache
        self._memory_cache[cache_key] = (matched_df, meta, is_cached)

        return matched_df.copy(), meta.copy(), is_cached

    def get_summary(self, start_date: str = "2026-01-01", end_date: str = "2026-01-31", cutoff_hour: int = 11) -> Dict[str, Any]:
        df, meta, _ = self.get_processed_data(start_date, end_date, cutoff_hour)
        return MetricsCalculator.calculate_summary_kpis(df, meta)

    def get_timeseries(self, start_date: str = "2026-01-01", end_date: str = "2026-01-31", cutoff_hour: int = 11) -> Dict[str, Any]:
        df, meta, is_cached = self.get_processed_data(start_date, end_date, cutoff_hour)
        if df.empty:
            return {"points": [], "metadata": meta}

        # Convert to records
        points = []
        for _, row in df.iterrows():
            points.append({
                "startTime": row["startTime"],
                "settlementDate": row["settlementDate"],
                "settlementPeriod": int(row["settlementPeriod"]) if row.get("settlementPeriod") else None,
                "actual_mw": round(float(row["actual_mw"]), 1),
                "forecast_mw": round(float(row["forecast_mw"]), 1),
                "signed_error_mw": round(float(row["signed_error_mw"]), 1),
                "abs_error_mw": round(float(row["abs_error_mw"]), 1),
                "publishTime": row["publishTime"],
                "cutoffTime": row["cutoffTime"]
            })

        return {
            "points": points,
            "metadata": meta,
            "is_cached": is_cached
        }

    def get_accuracy(self, start_date: str = "2026-01-01", end_date: str = "2026-01-31", cutoff_hour: int = 11) -> Dict[str, Any]:
        df, meta, _ = self.get_processed_data(start_date, end_date, cutoff_hour)
        overall = MetricsCalculator.calculate_summary_kpis(df, meta)
        daily = MetricsCalculator.calculate_daily_metrics(df)
        hourly = MetricsCalculator.calculate_hourly_profile(df)
        distribution = MetricsCalculator.calculate_error_distribution(df)
        largest_errors = MetricsCalculator.get_largest_error_intervals(df, top_n=10)

        return {
            "overall_kpis": overall,
            "daily_metrics": daily,
            "hourly_profile": hourly,
            "error_distribution": distribution,
            "largest_errors": largest_errors
        }

    def get_publication_history(self, start_date: str = "2026-01-01", end_date: str = "2026-01-31", cutoff_hour: int = 11) -> Dict[str, Any]:
        df, meta, _ = self.get_processed_data(start_date, end_date, cutoff_hour)
        return MetricsCalculator.calculate_publication_history(df, meta)

    def get_records(
        self,
        start_date: str = "2026-01-01",
        end_date: str = "2026-01-31",
        cutoff_hour: int = 11,
        page: int = 1,
        page_size: int = 50,
        sort_by: str = "startTime",
        sort_desc: bool = False,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        df, _, _ = self.get_processed_data(start_date, end_date, cutoff_hour)
        if df.empty:
            return {"total_records": 0, "page": page, "page_size": page_size, "total_pages": 0, "records": []}

        # Apply search if given
        if search:
            search_str = search.lower()
            mask = (
                df["startTime"].str.lower().str.contains(search_str) |
                df["settlementDate"].str.lower().str.contains(search_str) |
                df["publishTime"].str.lower().str.contains(search_str)
            )
            df = df[mask]

        # Sorting
        if sort_by in df.columns:
            df = df.sort_values(sort_by, ascending=not sort_desc)
        else:
            df = df.sort_values("start_dt", ascending=not sort_desc)

        total_records = len(df)
        total_pages = max(1, (total_records + page_size - 1) // page_size)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size

        sliced = df.iloc[start_idx:end_idx]
        records = []
        for idx, row in sliced.iterrows():
            records.append({
                "id": int(idx) + 1,
                "startTime": row["startTime"],
                "settlementDate": row["settlementDate"],
                "settlementPeriod": int(row["settlementPeriod"]) if row.get("settlementPeriod") else None,
                "actual_mw": round(float(row["actual_mw"]), 1),
                "forecast_mw": round(float(row["forecast_mw"]), 1),
                "signed_error_mw": round(float(row["signed_error_mw"]), 1),
                "abs_error_mw": round(float(row["abs_error_mw"]), 1),
                "publishTime": row["publishTime"],
                "cutoffTime": row["cutoffTime"]
            })

        return {
            "total_records": total_records,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "records": records
        }

    def get_data_status(self) -> Dict[str, Any]:
        meta = self.client.get_cache_metadata()
        live_ok = self.client.check_live_connectivity()
        
        # Get count stats from default January dataset
        try:
            _, pipeline_meta, is_cached = self.get_processed_data()
            matched_count = pipeline_meta.get("matched_intervals", 0)
            missing_count = pipeline_meta.get("missing_intervals", 0)
        except Exception:
            matched_count = 0
            missing_count = 0
            is_cached = meta.get("is_cached", False)

        return {
            "api_connection_status": "Online (Live Elexon BMRS API Accessible)" if live_ok else "Offline / Protected (Using High-Fidelity Local Cache)",
            "last_refresh_timestamp": meta.get("last_updated"),
            "is_cached": is_cached,
            "actual_records_count": meta.get("actual_wind_records", 0),
            "forecast_records_count": meta.get("forecast_records", 0),
            "matched_intervals_count": matched_count,
            "missing_intervals_count": missing_count,
            "period": meta.get("period", "January 2026"),
            "elexon_live_accessible": live_ok,
            "message": "Serving genuine Elexon BMRS national wind actuals (FUELHH) and forecasts (WINDFOR)."
        }

# Global singleton pipeline instance
pipeline_instance = DataPipeline()
