import numpy as np
import pandas as pd
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class MetricsCalculator:
    """
    Calculates statistical, quantitative, and economic accuracy metrics for wind power forecasts.
    """

    @staticmethod
    def calculate_summary_kpis(df: pd.DataFrame, meta: Dict[str, Any]) -> Dict[str, Any]:
        """Calculates high-level executive KPIs from matched forecast-actual dataframe."""
        if df.empty:
            return {
                "total_actual_generation_mwh": 0.0,
                "total_forecast_generation_mwh": 0.0,
                "avg_actual_generation_mw": 0.0,
                "avg_forecast_generation_mw": 0.0,
                "mae_mw": 0.0,
                "rmse_mw": 0.0,
                "bias_mw": 0.0,
                "wape_pct": 0.0,
                "total_absolute_error_mwh": 0.0,
                "total_intervals": meta.get("total_expected_intervals", 0),
                "matched_intervals": 0,
                "missing_intervals": meta.get("total_expected_intervals", 0),
                "coverage_pct": 0.0,
                "day_ahead_cutoff_hour": meta.get("cutoff_hour", 11)
            }

        actual = df["actual_mw"].to_numpy()
        forecast = df["forecast_mw"].to_numpy()
        error = forecast - actual
        abs_error = np.abs(error)

        # 30-min settlement intervals: MWh = MW * 0.5 hours
        total_actual_mwh = float(np.sum(actual) * 0.5)
        total_forecast_mwh = float(np.sum(forecast) * 0.5)
        total_abs_error_mwh = float(np.sum(abs_error) * 0.5)

        avg_actual_mw = float(np.mean(actual))
        avg_forecast_mw = float(np.mean(forecast))

        mae = float(np.mean(abs_error))
        rmse = float(np.sqrt(np.mean(error ** 2)))
        bias = float(np.mean(error))

        # WAPE = sum(|F - A|) / sum(A) * 100%
        sum_actual = float(np.sum(actual))
        wape = float((np.sum(abs_error) / sum_actual) * 100.0) if sum_actual > 0 else 0.0

        return {
            "total_actual_generation_mwh": round(total_actual_mwh, 1),
            "total_forecast_generation_mwh": round(total_forecast_mwh, 1),
            "avg_actual_generation_mw": round(avg_actual_mw, 1),
            "avg_forecast_generation_mw": round(avg_forecast_mw, 1),
            "mae_mw": round(mae, 1),
            "rmse_mw": round(rmse, 1),
            "bias_mw": round(bias, 1),
            "wape_pct": round(wape, 2),
            "total_absolute_error_mwh": round(total_abs_error_mwh, 1),
            "total_intervals": meta.get("total_expected_intervals", len(df)),
            "matched_intervals": meta.get("matched_intervals", len(df)),
            "missing_intervals": meta.get("missing_intervals", 0),
            "coverage_pct": meta.get("coverage_pct", 100.0),
            "day_ahead_cutoff_hour": meta.get("cutoff_hour", 11)
        }

    @staticmethod
    def calculate_daily_metrics(df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Calculates accuracy metrics aggregated by calendar day."""
        if df.empty:
            return []

        daily_list = []
        for date_str, group in df.groupby("settlementDate"):
            act = group["actual_mw"].to_numpy()
            fc = group["forecast_mw"].to_numpy()
            err = fc - act
            abs_err = np.abs(err)

            sum_act = float(np.sum(act))
            wape = float((np.sum(abs_err) / sum_act) * 100.0) if sum_act > 0 else 0.0

            daily_list.append({
                "date": date_str,
                "actual_mwh": round(float(np.sum(act) * 0.5), 1),
                "forecast_mwh": round(float(np.sum(fc) * 0.5), 1),
                "mae_mw": round(float(np.mean(abs_err)), 1),
                "rmse_mw": round(float(np.sqrt(np.mean(err ** 2))), 1),
                "bias_mw": round(float(np.mean(err)), 1),
                "wape_pct": round(wape, 2),
                "interval_count": len(group)
            })

        return sorted(daily_list, key=lambda x: x["date"])

    @staticmethod
    def calculate_hourly_profile(df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Computes diurnal profile across the 24 hours of the day."""
        if df.empty:
            return []

        df_copy = df.copy()
        df_copy["hour"] = df_copy["start_dt"].dt.hour
        
        hourly = []
        for hr, grp in df_copy.groupby("hour"):
            act = grp["actual_mw"].to_numpy()
            fc = grp["forecast_mw"].to_numpy()
            err = fc - act
            abs_err = np.abs(err)

            hourly.append({
                "hour": int(hr),
                "avg_actual_mw": round(float(np.mean(act)), 1),
                "avg_forecast_mw": round(float(np.mean(fc)), 1),
                "mae_mw": round(float(np.mean(abs_err)), 1),
                "bias_mw": round(float(np.mean(err)), 1)
            })

        return sorted(hourly, key=lambda x: x["hour"])

    @staticmethod
    def calculate_error_distribution(df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Computes histogram bins for signed forecast errors."""
        if df.empty:
            return []

        errors = df["signed_error_mw"].dropna().to_numpy()
        # Define sensible MW bins for national wind fleet (0 - 25,000 MW scale)
        bins = [-10000, -5000, -3000, -1500, -500, 500, 1500, 3000, 5000, 10000]
        bin_labels = [
            "< -5,000 MW (Severe Under-forecast)",
            "-5,000 to -3,000 MW",
            "-3,000 to -1,500 MW",
            "-1,500 to -500 MW",
            "-500 to +500 MW (Accurate / On-target)",
            "+500 to +1,500 MW",
            "+1,500 to +3,000 MW",
            "+3,000 to +5,000 MW",
            "> +5,000 MW (Severe Over-forecast)"
        ]

        counts, _ = np.histogram(errors, bins=bins)
        
        result = []
        for i, count in enumerate(counts):
            result.append({
                "bin_range": bin_labels[i],
                "bin_start": float(bins[i]),
                "bin_end": float(bins[i+1]),
                "count": int(count)
            })
        return result

    @staticmethod
    def get_largest_error_intervals(df: pd.DataFrame, top_n: int = 10) -> List[Dict[str, Any]]:
        """Identifies settlement intervals with the highest absolute forecast error."""
        if df.empty:
            return []

        top_df = df.sort_values("abs_error_mw", ascending=False).head(top_n)
        items = []
        for _, row in top_df.iterrows():
            signed_err = float(row["signed_error_mw"])
            implication = (
                "Over-forecast: Procured excess power day-ahead; wind did not deliver; required costly cash-out or balancing mechanism spill."
                if signed_err > 0
                else "Under-forecast: Wind overperformed; day-ahead procurement was higher than needed; excess renewable power had to be absorbed/curtailed."
            )
            items.append({
                "startTime": row["startTime"],
                "settlementPeriod": int(row.get("settlementPeriod", 0)) if row.get("settlementPeriod") else None,
                "actual_mw": round(float(row["actual_mw"]), 1),
                "forecast_mw": round(float(row["forecast_mw"]), 1),
                "signed_error_mw": round(signed_err, 1),
                "abs_error_mw": round(float(row["abs_error_mw"]), 1),
                "publishTime": row["publishTime"],
                "implication": implication
            })
        return items

    @staticmethod
    def calculate_publication_history(df: pd.DataFrame, meta: Dict[str, Any]) -> Dict[str, Any]:
        """Analyzes publication versions selected and confirms leakage prevention."""
        if df.empty:
            return {
                "decision_cutoff_hour": meta.get("cutoff_hour", 11),
                "cutoff_description": meta.get("cutoff_rule", ""),
                "total_matched": 0,
                "versions": [],
                "leakage_prevented_count": 0,
                "methodology_notes": [
                    "No records matched."
                ]
            }

        total = len(df)
        pub_counts = df["publishTime"].value_counts()
        
        versions = []
        for pub_time, count in pub_counts.head(10).items():
            pct = round((count / total) * 100, 1)
            # Extract time of day for label
            time_part = pub_time.split("T")[1][:5] if "T" in pub_time else ""
            desc = f"Forecast issued at {time_part} UTC"
            versions.append({
                "publishTime": pub_time,
                "count": int(count),
                "percentage": pct,
                "description": desc
            })

        cutoff_hr = meta.get("cutoff_hour", 11)
        notes = [
            f"Day-ahead procurement decision cutoff is set to {cutoff_hr:02d}:00 UTC on day D-1.",
            "Forecasts published after the cutoff are strictly excluded to model authentic auction bid conditions.",
            f"Successfully prevented {meta.get('leakage_prevented_count', 0)} future forecast runs from leaking into procurement decisions.",
            "National Grid ESO WINDFOR hourly predictions are mapped to UK 30-minute settlement periods."
        ]

        return {
            "decision_cutoff_hour": cutoff_hr,
            "cutoff_description": meta.get("cutoff_rule", f"Latest forecast published <= (D-1) {cutoff_hr:02d}:00 UTC"),
            "total_matched": total,
            "versions": versions,
            "leakage_prevented_count": meta.get("leakage_prevented_count", 0),
            "methodology_notes": notes
        }
