import {
  SummaryKPIs,
  TimeseriesResponse,
  AccuracyResponse,
  PublicationHistoryResponse,
  RecordsResponse,
  DataStatusResponse,
} from '../types';

const API_BASE = import.meta.env.VITE_API_URL || '';

export const api = {
  async fetchSummary(start = '2026-01-01', end = '2026-01-31', cutoff = 11): Promise<SummaryKPIs> {
    const params = new URLSearchParams({ start, end, cutoff: cutoff.toString() });
    const res = await fetch(`${API_BASE}/api/summary?${params}`);
    if (!res.ok) throw new Error(`Summary API failed: ${res.statusText}`);
    return res.json();
  },

  async fetchTimeseries(start = '2026-01-01', end = '2026-01-31', cutoff = 11): Promise<TimeseriesResponse> {
    const params = new URLSearchParams({ start, end, cutoff: cutoff.toString() });
    const res = await fetch(`${API_BASE}/api/timeseries?${params}`);
    if (!res.ok) throw new Error(`Timeseries API failed: ${res.statusText}`);
    return res.json();
  },

  async fetchAccuracy(start = '2026-01-01', end = '2026-01-31', cutoff = 11): Promise<AccuracyResponse> {
    const params = new URLSearchParams({ start, end, cutoff: cutoff.toString() });
    const res = await fetch(`${API_BASE}/api/accuracy?${params}`);
    if (!res.ok) throw new Error(`Accuracy API failed: ${res.statusText}`);
    return res.json();
  },

  async fetchPublicationHistory(start = '2026-01-01', end = '2026-01-31', cutoff = 11): Promise<PublicationHistoryResponse> {
    const params = new URLSearchParams({ start, end, cutoff: cutoff.toString() });
    const res = await fetch(`${API_BASE}/api/publication-history?${params}`);
    if (!res.ok) throw new Error(`Publication history API failed: ${res.statusText}`);
    return res.json();
  },

  async fetchRecords(
    start = '2026-01-01',
    end = '2026-01-31',
    cutoff = 11,
    page = 1,
    pageSize = 50,
    sortBy = 'startTime',
    sortDesc = false,
    search?: string
  ): Promise<RecordsResponse> {
    const params = new URLSearchParams({
      start,
      end,
      cutoff: cutoff.toString(),
      page: page.toString(),
      page_size: pageSize.toString(),
      sort_by: sortBy,
      sort_desc: sortDesc.toString(),
    });
    if (search && search.trim()) {
      params.append('search', search.trim());
    }
    const res = await fetch(`${API_BASE}/api/records?${params}`);
    if (!res.ok) throw new Error(`Records API failed: ${res.statusText}`);
    return res.json();
  },

  async fetchDataStatus(): Promise<DataStatusResponse> {
    const res = await fetch(`${API_BASE}/api/data-status`);
    if (!res.ok) throw new Error(`Data status API failed: ${res.statusText}`);
    return res.json();
  },

  async triggerRefresh(start = '2026-01-01', end = '2026-01-31'): Promise<{ status: string; message: string }> {
    const params = new URLSearchParams({ start, end });
    const res = await fetch(`${API_BASE}/api/refresh?${params}`, { method: 'POST' });
    if (!res.ok) throw new Error(`Refresh API failed: ${res.statusText}`);
    return res.json();
  },

  getExportCsvUrl(start = '2026-01-01', end = '2026-01-31', cutoff = 11): string {
    const params = new URLSearchParams({ start, end, cutoff: cutoff.toString() });
    return `${API_BASE}/api/export/csv?${params}`;
  }
};
