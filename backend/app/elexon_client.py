import json
import logging
import time
import urllib.request
import urllib.error
from datetime import datetime
from typing import List, Dict, Any, Tuple
from pathlib import Path

from app.config import CACHE_DIR, ELEXON_FUELHH_URL, ELEXON_WINDFOR_URL

logger = logging.getLogger(__name__)

class ElexonClient:
    """Client for retrieving actual and forecasted generation from Elexon BMRS API with local caching."""

    def __init__(self, cache_dir: Path = CACHE_DIR):
        self.cache_dir = cache_dir
        self.actuals_cache_file = self.cache_dir / "actuals_raw.json"
        self.forecasts_cache_file = self.cache_dir / "forecasts_raw.json"
        self.metadata_cache_file = self.cache_dir / "cache_metadata.json"
        self.headers = {"User-Agent": "Gridbricks-Analytics-Platform/1.0 (Elexon BMRS Client)"}
        self._last_connectivity_check = 0.0
        self._last_connectivity_result = False

    def check_live_connectivity(self) -> bool:
        """Pings Elexon endpoint to test connectivity (cached for 30s to avoid repeated socket timeouts)."""
        now = time.time()
        if now - self._last_connectivity_check < 30.0:
            return self._last_connectivity_result

        try:
            url = f"{ELEXON_FUELHH_URL}?publishDateTimeFrom=2026-01-01T00:00:00Z&publishDateTimeTo=2026-01-01T00:30:00Z"
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=2) as resp:
                result = (resp.status == 200)
        except Exception as e:
            logger.warning("Elexon live connectivity check failed: %s", e)
            result = False

        self._last_connectivity_check = now
        self._last_connectivity_result = result
        return result

    def get_cache_metadata(self) -> Dict[str, Any]:
        """Reads metadata about the cached data."""
        if self.metadata_cache_file.exists():
            try:
                with open(self.metadata_cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error("Failed to read cache metadata: %s", e)
        return {
            "last_updated": None,
            "source": "None",
            "is_cached": False,
            "actual_wind_records": 0,
            "forecast_records": 0,
            "period": "January 2026"
        }

    def fetch_actuals(self, start_date: str = "2026-01-01", end_date: str = "2026-01-31", force_refresh: bool = False) -> Tuple[List[Dict[str, Any]], bool]:
        """
        Retrieves FUELHH actual generation records filtered to fuelType == 'WIND'.
        Returns (records, is_from_cache).
        """
        # If cache exists and not force_refresh, try loading from cache
        if not force_refresh and self.actuals_cache_file.exists():
            try:
                with open(self.actuals_cache_file, "r", encoding="utf-8") as f:
                    records = json.load(f)
                    logger.info("Loaded %d actual wind records from local cache.", len(records))
                    return records, True
            except Exception as e:
                logger.warning("Error reading actuals cache, falling back to live retrieval: %s", e)

        # Retrieve live from Elexon
        # Need up to next day 01:00Z to capture settlement period 48 of the end date
        url = f"{ELEXON_FUELHH_URL}?publishDateTimeFrom={start_date}T00:00:00Z&publishDateTimeTo=2026-02-01T01:00:00Z"
        logger.info("Fetching actuals live from Elexon: %s", url)
        try:
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=60) as resp:
                raw_data = json.loads(resp.read().decode("utf-8"))
            
            # Filter strictly to WIND
            wind_actuals = [d for d in raw_data if d.get("fuelType") == "WIND"]
            
            # Persist to cache
            with open(self.actuals_cache_file, "w", encoding="utf-8") as f:
                json.dump(wind_actuals, f, indent=2)
            
            self._update_metadata(actuals_count=len(wind_actuals))
            return wind_actuals, False

        except Exception as e:
            logger.error("Failed to fetch live FUELHH actuals from Elexon: %s", e)
            # Fallback to cache if available
            if self.actuals_cache_file.exists():
                logger.info("Falling back to existing cache despite live error.")
                with open(self.actuals_cache_file, "r", encoding="utf-8") as f:
                    return json.load(f), True
            raise RuntimeError(f"Unable to retrieve actuals from live API or cache: {e}")

    def fetch_forecasts(self, start_date: str = "2026-01-01", end_date: str = "2026-01-31", force_refresh: bool = False) -> Tuple[List[Dict[str, Any]], bool]:
        """
        Retrieves WINDFOR wind generation forecast records.
        Returns (records, is_from_cache).
        """
        if not force_refresh and self.forecasts_cache_file.exists():
            try:
                with open(self.forecasts_cache_file, "r", encoding="utf-8") as f:
                    records = json.load(f)
                    logger.info("Loaded %d forecast records from local cache.", len(records))
                    return records, True
            except Exception as e:
                logger.warning("Error reading forecasts cache, falling back to live retrieval: %s", e)

        # Retrieve live: start from 2025-12-30 to ensure D-1 forecasts for Jan 1 are captured
        url = f"{ELEXON_WINDFOR_URL}?publishDateTimeFrom=2025-12-30T00:00:00Z&publishDateTimeTo={end_date}T23:59:59Z"
        logger.info("Fetching forecasts live from Elexon: %s", url)
        try:
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=60) as resp:
                raw_forecasts = json.loads(resp.read().decode("utf-8"))

            with open(self.forecasts_cache_file, "w", encoding="utf-8") as f:
                json.dump(raw_forecasts, f, indent=2)

            self._update_metadata(forecasts_count=len(raw_forecasts))
            return raw_forecasts, False

        except Exception as e:
            logger.error("Failed to fetch live WINDFOR forecasts from Elexon: %s", e)
            if self.forecasts_cache_file.exists():
                logger.info("Falling back to existing cache despite live error.")
                with open(self.forecasts_cache_file, "r", encoding="utf-8") as f:
                    return json.load(f), True
            raise RuntimeError(f"Unable to retrieve forecasts from live API or cache: {e}")

    def _update_metadata(self, actuals_count: int = None, forecasts_count: int = None):
        meta = self.get_cache_metadata()
        meta["last_updated"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        meta["source"] = "Elexon Insights BMRS API v1"
        meta["is_cached"] = True
        if actuals_count is not None:
            meta["actual_wind_records"] = actuals_count
        if forecasts_count is not None:
            meta["forecast_records"] = forecasts_count
        with open(self.metadata_cache_file, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)
