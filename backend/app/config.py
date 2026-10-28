import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CACHE_DIR = DATA_DIR / "cache"
FIXTURES_DIR = DATA_DIR / "sample_fixtures"

CACHE_DIR.mkdir(parents=True, exist_ok=True)
FIXTURES_DIR.mkdir(parents=True, exist_ok=True)

# Elexon API Endpoints
DEFAULT_ELEXON_BASE = "https://data.elexon.co.uk/bmrs/api/v1/datasets"
ELEXON_FUELHH_URL = os.getenv("ELEXON_FUELHH_URL", f"{DEFAULT_ELEXON_BASE}/FUELHH/stream")
ELEXON_WINDFOR_URL = os.getenv("ELEXON_WINDFOR_URL", f"{DEFAULT_ELEXON_BASE}/WINDFOR/stream")

# Procurement Market Parameters
DEFAULT_CUTOFF_HOUR = int(os.getenv("DAY_AHEAD_CUTOFF_HOUR", "11"))  # 11:00 UTC on D-1
DEFAULT_START_DATE = "2026-01-01"
DEFAULT_END_DATE = "2026-01-31"

# Server & CORS
PORT = int(os.getenv("PORT", "8000"))
HOST = os.getenv("HOST", "0.0.0.0")
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000,https://*.vercel.app"
).split(",")
