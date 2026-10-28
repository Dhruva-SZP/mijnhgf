import React, { useState, useEffect, useCallback } from 'react';
import { api } from './services/api';
import {
  SummaryKPIs,
  TimeseriesPoint,
  AccuracyResponse,
  PublicationHistoryResponse,
  RecordsResponse,
  DataStatusResponse,
} from './types';

import { Header } from './components/Header';
import { ExecutiveOverview } from './components/ExecutiveOverview';
import { ActualVsForecastChart } from './components/ActualVsForecastChart';
import { ErrorAnalysis } from './components/ErrorAnalysis';
import { PublicationHistory } from './components/PublicationHistory';
import { DetailedDataTable } from './components/DetailedDataTable';
import { DataStatusModal } from './components/DataStatusModal';
import { AlertCircle, RefreshCw, Info, ExternalLink } from 'lucide-react';

export const App: React.FC = () => {
  // Global filter state
  const [startDate, setStartDate] = useState('2026-01-01');
  const [endDate, setEndDate] = useState('2026-01-31');
  const [cutoffHour, setCutoffHour] = useState(11); // 11:00 UTC D-1 default

  // Records table state
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(50);
  const [sortBy, setSortBy] = useState('startTime');
  const [sortDesc, setSortDesc] = useState(false);
  const [search, setSearch] = useState('');

  // Data state
  const [kpis, setKpis] = useState<SummaryKPIs | null>(null);
  const [timeseries, setTimeseries] = useState<TimeseriesPoint[]>([]);
  const [accuracy, setAccuracy] = useState<AccuracyResponse | null>(null);
  const [pubHistory, setPubHistory] = useState<PublicationHistoryResponse | null>(null);
  const [recordsData, setRecordsData] = useState<RecordsResponse | null>(null);
  const [dataStatus, setDataStatus] = useState<DataStatusResponse | null>(null);

  // UI state
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isStatusModalOpen, setIsStatusModalOpen] = useState(false);

  // Load dashboard overview & analytics
  const loadDashboardData = useCallback(async () => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const [summaryRes, tsRes, accRes, histRes, statusRes] = await Promise.all([
        api.fetchSummary(startDate, endDate, cutoffHour),
        api.fetchTimeseries(startDate, endDate, cutoffHour),
        api.fetchAccuracy(startDate, endDate, cutoffHour),
        api.fetchPublicationHistory(startDate, endDate, cutoffHour),
        api.fetchDataStatus(),
      ]);

      setKpis(summaryRes);
      setTimeseries(tsRes.points);
      setAccuracy(accRes);
      setPubHistory(histRes);
      setDataStatus(statusRes);
    } catch (err: any) {
      console.error('Failed to load dashboard data:', err);
      setErrorMessage(
        err.message || 'Unable to connect to the Gridbricks Python backend. Ensure the backend server is running.'
      );
    } finally {
      setIsLoading(false);
    }
  }, [startDate, endDate, cutoffHour]);

  // Load granular table records
  const loadRecords = useCallback(async () => {
    try {
      const res = await api.fetchRecords(
        startDate,
        endDate,
        cutoffHour,
        page,
        pageSize,
        sortBy,
        sortDesc,
        search
      );
      setRecordsData(res);
    } catch (err: any) {
      console.error('Failed to load records:', err);
    }
  }, [startDate, endDate, cutoffHour, page, pageSize, sortBy, sortDesc, search]);

  useEffect(() => {
    loadDashboardData();
  }, [loadDashboardData]);

  useEffect(() => {
    loadRecords();
  }, [loadRecords]);

  // Handlers
  const handleDateChange = (start: string, end: string) => {
    setStartDate(start);
    setEndDate(end);
    setPage(1);
  };

  const handleCutoffChange = (cutoff: number) => {
    setCutoffHour(cutoff);
    setPage(1);
  };

  const handleSortChange = (column: string) => {
    if (sortBy === column) {
      setSortDesc(!sortDesc);
    } else {
      setSortBy(column);
      setSortDesc(false);
    }
    setPage(1);
  };

  const handleSearchChange = (newSearch: string) => {
    setSearch(newSearch);
    setPage(1);
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      await api.triggerRefresh(startDate, endDate);
      await loadDashboardData();
      await loadRecords();
    } catch (err: any) {
      alert(`Refresh error: ${err.message}`);
    } finally {
      setIsRefreshing(false);
    }
  };

  const csvExportUrl = api.getExportCsvUrl(startDate, endDate, cutoffHour);

  return (
    <div className="min-h-screen bg-[#0b1120] text-slate-100 flex flex-col">
      {/* Header with global controls */}
      <Header
        startDate={startDate}
        endDate={endDate}
        cutoffHour={cutoffHour}
        onDateChange={handleDateChange}
        onCutoffChange={handleCutoffChange}
        onOpenDataStatus={() => setIsStatusModalOpen(true)}
        onRefresh={handleRefresh}
        isRefreshing={isRefreshing}
        dataStatus={dataStatus}
        csvExportUrl={csvExportUrl}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-6 space-y-6">
        {/* Error notification banner */}
        {errorMessage && (
          <div className="p-4 rounded-xl bg-rose-950/60 border border-rose-800 text-rose-200 flex items-start justify-between gap-3 text-xs">
            <div className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-rose-400 shrink-0" />
              <span>{errorMessage}</span>
            </div>
            <button
              onClick={loadDashboardData}
              className="px-3 py-1 rounded bg-rose-900 hover:bg-rose-800 text-white font-medium transition-colors"
            >
              Retry
            </button>
          </div>
        )}

        {/* Section A: Executive Overview & KPIs */}
        <ExecutiveOverview kpis={kpis} isLoading={isLoading} />

        {/* Section B: Time-Series Chart */}
        <ActualVsForecastChart data={timeseries} isLoading={isLoading} />

        {/* Section C: Error Analysis & Risk Evaluation */}
        <ErrorAnalysis accuracy={accuracy} isLoading={isLoading} />

        {/* Section D: Publication History & Cutoff Audit Trail */}
        <PublicationHistory history={pubHistory} isLoading={isLoading} />

        {/* Section E: Detailed Granular Records Table */}
        <DetailedDataTable
          recordsData={recordsData}
          isLoading={isLoading}
          page={page}
          pageSize={pageSize}
          sortBy={sortBy}
          sortDesc={sortDesc}
          search={search}
          onPageChange={setPage}
          onPageSizeChange={(newSize) => {
            setPageSize(newSize);
            setPage(1);
          }}
          onSortChange={handleSortChange}
          onSearchChange={handleSearchChange}
        />
      </main>

      {/* Section F: Data Status Modal */}
      <DataStatusModal
        isOpen={isStatusModalOpen}
        onClose={() => setIsStatusModalOpen(false)}
        status={dataStatus}
        onRefresh={handleRefresh}
        isRefreshing={isRefreshing}
      />

      {/* Enterprise Footer */}
      <footer className="border-t border-slate-800/80 bg-slate-950 py-6 px-6 mt-12 text-xs text-slate-500">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div>
            <span className="font-semibold text-slate-400">Gridbricks Challenge Application</span> • UK Electricity Day-Ahead Wind Forecasting & Procurement
            <div className="text-[11px] text-slate-600 mt-1">
              Data strictly from Elexon BMRS (<code>FUELHH</code> wind actuals and <code>WINDFOR</code> forecasts) • January 2026.
            </div>
          </div>

          <div className="text-right text-[11px] text-slate-500">
            <div>Built with React, FastAPI, pandas, NumPy, Recharts & Tailwind CSS</div>
            <div className="text-slate-600 mt-0.5">Assisted by AI tools in accordance with challenge guidelines.</div>
          </div>
        </div>
      </footer>
    </div>
  );
};
