import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import CORS_ORIGINS
from app.routes import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("gridbricks-backend")

app = FastAPI(
    title="Gridbricks Wind Procurement Analytics API",
    description="Enterprise REST API for day-ahead electricity procurement decision support using Elexon BMRS data.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for local dev, preview and deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
def root():
    return {
        "platform": "Gridbricks Full-Stack SWE Challenge API",
        "market": "UK Wholesale Electricity Day-Ahead Market",
        "documentation": "/docs",
        "health": "/api/health",
        "summary": "/api/summary",
        "timeseries": "/api/timeseries",
        "accuracy": "/api/accuracy",
        "records": "/api/records",
        "data_status": "/api/data-status"
    }

if __name__ == "__main__":
    import uvicorn
    from app.config import PORT, HOST
    uvicorn.run("app.main:app", host=HOST, port=PORT, reload=True)
