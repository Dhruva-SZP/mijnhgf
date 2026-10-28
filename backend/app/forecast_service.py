import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple, Optional
import pandas as pd

from app.config import DEFAULT_CUTOFF_HOUR

logger = logging.getLogger(__name__)

class ForecastSelectionService:
    """
    Implements defensible forecast-selection and matching methodology for UK wholesale day-ahead procurement.
    
    Domain Logic:
    1. Delivery intervals in UK wholesale market are 30-minute settlement periods (48 periods/day in January UTC).
    2. National Grid ESO WINDFOR forecasts are published at hourly resolution representing expected average MW.
    3. Day-Ahead purchasing decisions for delivery day D are finalized on day D-1 before market cutoff (e.g., 11:00 UTC).
    4. Any forecast published after (D-1) at cutoff_hour:00:00Z is strictly excluded to prevent future data leakage.
    5. The latest forecast published on or before the cutoff is selected.
    """

    def __init__(self, cutoff_hour: int = DEFAULT_CUTOFF_HOUR):
        self.cutoff_hour = cutoff_hour

    def process_and_match(
        self,
        actual_records: List[Dict[str, Any]],
        forecast_records: List[Dict[str, Any]],
        start_date: str = "2026-01-01",
        end_date: str = "2026-01-31",
        cutoff_hour: Optional[int] = None
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Normalizes actuals and forecasts, matches them strictly by settlement interval,
        and enforces the day-ahead decision cutoff.
        
        Returns:
            (matched_df, metadata_dict)
        """
        active_cutoff_hour = cutoff_hour if cutoff_hour is not None else self.cutoff_hour
        
        if not actual_records or not forecast_records:
            logger.warning("Empty records provided to forecast matching engine.")
            return pd.DataFrame(), {
                "total_expected_intervals": 0,
                "matched_intervals": 0,
                "missing_intervals": 0,
                "coverage_pct": 0.0,
                "leakage_prevented_count": 0,
                "cutoff_hour": active_cutoff_hour
            }

        # 1. Normalize actuals
        df_act = pd.DataFrame(actual_records)
        df_act = df_act[df_act.get("fuelType", "WIND") == "WIND"].copy()
        df_act["start_dt"] = pd.to_datetime(df_act["startTime"], utc=True)
        
        # Deduplicate actuals by startTime
        if "publishTime" in df_act.columns:
            df_act = df_act.sort_values("publishTime", ascending=False)
        df_act = df_act.drop_duplicates(subset=["start_dt"]).sort_values("start_dt")

        # Filter strictly within requested delivery bounds
        start_bound = pd.Timestamp(f"{start_date} 00:00:00", tz="UTC")
        end_bound = pd.Timestamp(f"{end_date} 23:59:59", tz="UTC")
        df_act = df_act[(df_act["start_dt"] >= start_bound) & (df_act["start_dt"] <= end_bound)].copy()

        # 2. Normalize forecasts
        df_fc = pd.DataFrame(forecast_records).copy()
        df_fc["start_dt"] = pd.to_datetime(df_fc["startTime"], utc=True)
        df_fc["pub_dt"] = pd.to_datetime(df_fc["publishTime"], utc=True)
        df_fc["generation"] = pd.to_numeric(df_fc["generation"], errors="coerce")
        df_fc = df_fc.dropna(subset=["generation", "start_dt", "pub_dt"])

        # 3. Perform matching with day-ahead cutoff enforcement
        matched_rows = []
        leakage_prevented_count = 0
        
        # Pre-group forecasts by start_dt for fast indexing
        fc_by_target = {}
        for target_time, group in df_fc.groupby("start_dt"):
            fc_by_target[target_time] = group.sort_values("pub_dt", ascending=False)

        for _, act_row in df_act.iterrows():
            delivery_time = act_row["start_dt"]
            delivery_date = delivery_time.date()
            
            # Decision Cutoff = (delivery_date - 1 day) at active_cutoff_hour:00:00 UTC
            decision_day = delivery_date - timedelta(days=1)
            cutoff_dt = pd.Timestamp(decision_day, tz="UTC") + pd.Timedelta(hours=active_cutoff_hour)
            
            # Wind forecasts are hourly; floor delivery time to matching hour
            fc_target_hour = delivery_time.floor("h")
            
            target_forecasts = fc_by_target.get(fc_target_hour)
            if target_forecasts is not None and not target_forecasts.empty:
                # Candidates published on or before cutoff
                valid_candidates = target_forecasts[target_forecasts["pub_dt"] <= cutoff_dt]
                
                # Check how many newer forecasts were excluded due to cutoff
                post_cutoff_forecasts = target_forecasts[target_forecasts["pub_dt"] > cutoff_dt]
                leakage_prevented_count += len(post_cutoff_forecasts)

                if not valid_candidates.empty:
                    # Best is the latest published before cutoff
                    best_fc = valid_candidates.iloc[0]
                    
                    matched_rows.append({
                        "startTime": act_row["startTime"],
                        "start_dt": delivery_time,
                        "settlementDate": str(act_row.get("settlementDate", delivery_date.isoformat())),
                        "settlementPeriod": int(act_row.get("settlementPeriod", 0)) if act_row.get("settlementPeriod") else None,
                        "actual_mw": float(act_row["generation"]),
                        "forecast_mw": float(best_fc["generation"]),
                        "publishTime": best_fc["publishTime"],
                        "publish_dt": best_fc["pub_dt"],
                        "cutoffTime": cutoff_dt.isoformat(),
                        "post_cutoff_updates_available": len(post_cutoff_forecasts)
                    })

        matched_df = pd.DataFrame(matched_rows)
        
        if not matched_df.empty:
            matched_df["signed_error_mw"] = matched_df["forecast_mw"] - matched_df["actual_mw"]
            matched_df["abs_error_mw"] = matched_df["signed_error_mw"].abs()
            matched_df = matched_df.sort_values("start_dt").reset_index(drop=True)

        # Expected intervals: 48 half-hours per day in range
        num_days = (pd.to_datetime(end_date) - pd.to_datetime(start_date)).days + 1
        expected_intervals = num_days * 48
        matched_count = len(matched_df)
        missing_count = max(0, expected_intervals - matched_count)
        coverage_pct = round((matched_count / expected_intervals) * 100, 2) if expected_intervals > 0 else 0.0

        meta = {
            "total_expected_intervals": expected_intervals,
            "matched_intervals": matched_count,
            "missing_intervals": missing_count,
            "coverage_pct": coverage_pct,
            "leakage_prevented_count": leakage_prevented_count,
            "cutoff_hour": active_cutoff_hour,
            "cutoff_rule": f"Latest forecast published on or before (D-1) at {active_cutoff_hour:02d}:00 UTC",
            "settlement_resolution": "30-minute settlement period (HH)"
        }

        return matched_df, meta
