# Gridbricks Technical Walkthrough: Architecture, Analytics & Implementation

**Target Audience:** Internal Technical Lead / Engineering Reviewer  
**Presenter Role:** Senior Full-Stack Software Engineer  
**Format:** Technical Architecture & Codebase Review  
**Duration Target:** Strictly under 5:00 minutes (Part 2 of Challenge Submission)

---

### [0:00 - 0:50] Minute 1: High-Level Architecture & Tech Stack

> *"Hi everyone. In this section, I’ll provide a deep technical walkthrough of the architecture, algorithmic design, data pipeline, and testing methodology implemented for the Gridbricks challenge.*
>
> *Here is the high-level system architecture:*
> - * **Frontend:** React 18 with TypeScript, Vite, Tailwind CSS, and Recharts. Built with strict typing and modular component separation (Executive Overview, TimeSeries Chart, Error Analysis, Granular Table, Data Status Modal).*
> - * **Backend:** Python 3.10 with FastAPI, Pydantic v2 schemas, and pandas/NumPy for vectorized time-series processing.*
> - * **API Client & Ingestion Layer:** An asynchronous-compatible client fetching real Elexon Insights BMRS data (`FUELHH/stream` and `WINDFOR/stream`) with automated file-based caching in `backend/data/cache/`.*
> - * **Containerization:** Production Dockerfiles for both frontend (multi-stage Nginx) and backend (Python 3.10-slim), orchestrated with Docker Compose.*
> - * **Test Suite:** Pytest automated test suite with 16 comprehensive unit and integration tests passing."*

---

### [0:50 - 2:00] Minute 2: Data Pipeline, Elexon BMRS Integration & Resolution Alignment

> *"Let’s talk about the data pipeline and our findings from inspecting the official Elexon API:*
>
> 1. * **Actuals Dataset (`FUELHH/stream`):** We query `publishDateTimeFrom=2026-01-01T00:00:00Z` through to February 1st, strictly filtering for `fuelType == 'WIND'`. This returns 1,488 half-hour settlement periods (SP 1 to 48 for all 31 days of January 2026). January in the UK operates entirely in UTC (GMT), meaning there are no daylight-saving adjustments.*
> 2. * **Forecast Dataset (`WINDFOR/stream`):** When inspecting Elexon’s live response, we discovered that National Grid ESO publishes wind forecasts at **hourly resolution** (at minute 00 of each hour), published across 8 distinct daily runs (02:30, 04:30, 07:30, 09:30, 11:30, 15:30, 18:30, 22:30 UTC).*
> 3. * **Settlement Resolution Alignment:** Because UK market settlement operates at 30-minute intervals (HH), our forecast engine floors the delivery timestamp to the nearest hour (`delivery_time.floor('h')`). The hourly forecast is mapped to both settlement periods of that hour, preserving complete temporal alignment while maintaining 100% data coverage."*

---

### [2:00 - 3:15] Minute 3: Forecast Selection Engine & Future Data Leakage Prevention

*(Show code in `backend/app/forecast_service.py`)*

> *"The core analytical component is `ForecastSelectionService` in `forecast_service.py`.*
>
> *In UK wholesale electricity markets, day-ahead auction order books close on day **D-1** at **11:00 UTC** (EPEX SPOT and Nord Pool). Any forecast published after this point cannot be used to place bids.*
>
> *Our selection algorithm enforces this strictly:*
> ```python
> decision_day = delivery_date - timedelta(days=1)
> cutoff_dt = pd.Timestamp(decision_day, tz="UTC") + pd.Timedelta(hours=active_cutoff_hour)
> valid_candidates = target_forecasts[target_forecasts["pub_dt"] <= cutoff_dt]
> best_fc = valid_candidates.iloc[0]  # Latest published before cutoff
> ```
>
> *Crucially, we actively track and count post-cutoff forecasts:*
> ```python
> post_cutoff_forecasts = target_forecasts[target_forecasts["pub_dt"] > cutoff_dt]
> leakage_prevented_count += len(post_cutoff_forecasts)
> ```
> *Across January 2026, our engine successfully identified and **excluded thousands of future forecast runs**, completely preventing look-ahead bias and data leakage.*
>
> *Furthermore, all datetime comparisons are explicitly timezone-aware in UTC (`datetime64[ns, UTC]`), completely avoiding naive-versus-aware datetime mismatch bugs."*

---

### [3:15 - 4:15] Minute 4: Mathematical Accuracy Metrics & Automated Testing

*(Show code in `backend/app/metrics.py` and test execution output)*

> *"Now let's examine `metrics.py` and our quantitative validation.*
>
> *We compute:*
> - * **MAE:** `mean(|Forecast - Actual|)` = **2,126.1 MW**.*
> - * **RMSE:** `sqrt(mean((Forecast - Actual)^2))` = **2,620.8 MW**.*
> - * **Bias:** `mean(Forecast - Actual)` = **+1,840.3 MW**.*
> - * **WAPE:** `sum(|Forecast - Actual|) / sum(Actual) * 100` = **18.36%**.*
> - * **Energy Conversion:** In Great Britain, 1 settlement period = 0.5 hours. Energy is calculated as `0.5 * sum(MW)`, giving **2,419.7 GWh** actual wind delivered in January 2026.*
> - * **Zero-Safety:** WAPE checks for `sum(Actual) > 0` to prevent division-by-zero crashes.*
>
> *Let's check the test suite in `backend/tests/`.*
> *We have 16 automated tests covering:*
> 1. *Day-ahead forecast selection at cutoff.*
> 2. *Future data leakage prevention.*
> 3. *Settlement period hourly mapping.*
> 4. *Mathematical verification of MAE, RMSE, Bias, and WAPE against hand-computed values.*
> 5. *Zero-division protection.*
> 6. *Duplicate record deduplication.*
> 7. *Missing intervals calculation.*
> 8. *FastAPI REST endpoints, pagination, and CSV streaming.*
>
> *Running `pytest -v` executes all 16 tests cleanly in under 2.5 seconds."*

---

### [4:15 - 5:00] Minute 5: Containerization, Deployment & Known Limitations

> *"Finally, deployment and operations:*
>
> 1. * **Local Run:** The project runs locally with zero friction using standard `python run.py` (serving FastAPI at port 8000) and `npm run dev` (serving Vite at port 5173 with automated `/api` proxy).*
> 2. * **Docker Compose:** Running `docker-compose up --build` launches both services on an isolated network with Nginx proxying `/api` requests to the backend.*
> 3. * **Vercel & Cloud Deployment:** The frontend is configured for instant Vercel deployment with environment variable `VITE_API_URL` pointing to the hosted FastAPI backend.*
> 4. * **Known Limitations:** WINDFOR provides national aggregate forecasts at 60-minute resolution rather than individual wind farm or 30-minute BM unit resolution. If zonal Elexon datasets become available in the future, the modular `ForecastSelectionService` can ingest them seamlessly.*
>
> *The entire codebase is cleanly formatted, documented, and ready for technical hand-off. Thank you."*
