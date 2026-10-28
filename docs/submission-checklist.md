# Gridbricks SWE Challenge — Final Submission Checklist

Follow this step-by-step checklist to prepare, verify, and submit your project to the Gridbricks hiring team.

---

## 1. Local Verification Checklist

- [ ] **Run Automated Backend Tests:**
  ```powershell
  cd C:\Users\ndhru\Downloads\gridbricks-challenge\backend
  pytest -v
  ```
  *Verify that all 16 tests pass without errors.*

- [ ] **Test Backend Locally:**
  ```powershell
  cd C:\Users\ndhru\Downloads\gridbricks-challenge\backend
  python run.py
  ```
  *Open http://localhost:8000/docs in your browser to verify Swagger OpenAPI documentation.*

- [ ] **Test Frontend Locally:**
  ```powershell
  cd C:\Users\ndhru\Downloads\gridbricks-challenge\frontend
  npm run dev
  ```
  *Open http://localhost:5173 in your browser and check:*
  - [ ] Executive KPI cards populate with genuine data.
  - [ ] Actual vs Forecast time-series chart renders and zooms.
  - [ ] Day-ahead cutoff selector changes metrics when toggled.
  - [ ] Error analysis tabs (Distribution, Daily, Hourly, Largest Errors) function smoothly.
  - [ ] Granular table search, sorting, and pagination work.
  - [ ] Export CSV downloads the dataset.
  - [ ] Data status modal opens and displays Elexon telemetry.

---

## 2. Docker Verification Checklist (Optional/If Docker Desktop is Running)

- [ ] **Launch Docker Compose:**
  ```powershell
  cd C:\Users\ndhru\Downloads\gridbricks-challenge
  docker-compose up --build
  ```
- [ ] Verify frontend is accessible on `http://localhost:3000`.
- [ ] Verify backend is accessible on `http://localhost:8000/api/health`.

---

## 3. Deployment Checklist

### A. Deploy Backend (FastAPI)
Options: Render, Railway, Heroku, or Fly.io (all support Python/Docker):
1. Create a new Web Service on Render / Railway pointing to the `backend/` directory or root `backend/Dockerfile`.
2. Environment Variables:
   - `PORT=8000`
   - `DAY_AHEAD_CUTOFF_HOUR=11`
   - `CORS_ORIGINS=https://*.vercel.app,http://localhost:5173`
3. Note your public backend URL (e.g., `https://gridbricks-backend.onrender.com`).

### B. Deploy Frontend (React / Vite on Vercel)
1. Push repository or import `frontend/` to Vercel.
2. In Vercel Project Settings:
   - **Framework Preset:** Vite
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
   - **Environment Variables:**
     - `VITE_API_URL=https://gridbricks-backend.onrender.com` (your backend URL)
3. Deploy and test the live Vercel URL.

---

## 4. GitHub Repository Preparation

- [x] **Created Anonymous Public GitHub Repo:**
  - Repository URL: `https://github.com/Dhruva-SZP/mijnhgf.git` (Anonymous repo name: `mijnhgf`)
  - Visibility: **Public**
- [ ] **Push Local Code to Remote:**
  ```powershell
  cd C:\Users\ndhru\Downloads\gridbricks-challenge
  git remote add origin https://github.com/Dhruva-SZP/mijnhgf.git
  git push -u origin main
  ```
- [ ] Check repository in browser (incognito) to ensure no secrets or local paths are exposed.

---

## 5. Unlisted YouTube Video Demo Preparation

- [ ] **Recording Tool:** OBS Studio, Loom, or Windows Game Bar (`Win + G`).
- [ ] **Max Total Duration:** Strictly under 10 minutes (ideally ~8-9 minutes total).
- [ ] **Part 1: Customer Presentation (<= 5:00 minutes)**
  - Script located at: `docs/customer-demo-script.md`
  - Pitch to UK energy utility procurement desk.
  - Highlight commercial risk, day-ahead auction gate closure, and +1,840 MW positive forecast bias.
- [ ] **Part 2: Technical Walkthrough (<= 5:00 minutes)**
  - Script located at: `docs/technical-walkthrough.md`
  - Walk through architecture, Elexon BMRS ingestion, 11:00 UTC D-1 cutoff, zero data leakage, and test suite.
- [ ] **Upload to YouTube:**
  - Set privacy to **Unlisted** (NOT Private).
  - Open YouTube link in an **Incognito / Private Window** to confirm video plays without login.

---

## 6. Official Submission Form

- [ ] **Form URL:** [https://forms.cloud.microsoft/r/FTX6K2bbnU](https://forms.cloud.microsoft/r/FTX6K2bbnU)
- [ ] Fill in required fields:
  1. Your Name & Email
  2. Public GitHub Repository Link (tested in incognito)
  3. Live Deployed Application Link (Vercel / Heroku, tested in incognito)
  4. Unlisted YouTube Video Demo Link (tested in incognito)
- [ ] Submit before deadline!
