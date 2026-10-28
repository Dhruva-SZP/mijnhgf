import React from 'react';
import { Wind, Clock, Download, Database, RefreshCw, Calendar, ShieldCheck } from 'lucide-react';
import { DataStatusResponse } from '../types';

interface HeaderProps {
  startDate: string;
  endDate: string;
  cutoffHour: number;
  onDateChange: (start: string, end: string) => void;
  onCutoffChange: (cutoff: number) => void;
  onOpenDataStatus: () => void;
  onRefresh: () => void;
  isRefreshing: boolean;
  dataStatus: DataStatusResponse | null;
  csvExportUrl: string;
}

export const Header: React.FC<HeaderProps> = ({
  startDate,
  endDate,
  cutoffHour,
  onDateChange,
  onCutoffChange,
  onOpenDataStatus,
  onRefresh,
  isRefreshing,
  dataStatus,
  csvExportUrl
}) => {
  const quickRanges = [
    { label: 'Full Month (Jan 1-31)', start: '2026-01-01', end: '2026-01-31' },
    { label: 'Wk 1 (Jan 1-7)', start: '2026-01-01', end: '2026-01-07' },
    { label: 'Wk 2 (Jan 8-14)', start: '2026-01-08', end: '2026-01-14' },
    { label: 'Wk 3 (Jan 15-21)', start: '2026-01-15', end: '2026-01-21' },
    { label: 'Wk 4 (Jan 22-31)', start: '2026-01-22', end: '2026-01-31' },
  ];

  return (
    <header className="border-b border-slate-800 bg-[#0f172a]/95 backdrop-blur sticky top-0 z-40 px-6 py-4">
      <div className="max-w-7xl mx-auto flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4">
        {/* Branding & Subtitle */}
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
            <Wind className="h-6 w-6 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold text-white tracking-tight">Gridbricks</h1>
              <span className="text-xs px-2 py-0.5 rounded-full bg-cyan-950 text-cyan-400 border border-cyan-800 font-mono">
                GB Wholesale Power
              </span>
            </div>
            <p className="text-xs text-slate-400">
              UK Day-Ahead Wind Generation Forecasting & Procurement Decision Platform
            </p>
          </div>
        </div>

        {/* Global Controls & Status */}
        <div className="flex flex-wrap items-center gap-3 w-full lg:w-auto justify-start lg:justify-end">
          {/* Day-Ahead Decision Cutoff Selector */}
          <div className="flex items-center gap-2 bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-xs">
            <Clock className="h-3.5 w-3.5 text-cyan-400" />
            <span className="text-slate-400 font-medium">D-1 Cutoff:</span>
            <select
              value={cutoffHour}
              onChange={(e) => onCutoffChange(Number(e.target.value))}
              className="bg-transparent text-cyan-300 font-semibold focus:outline-none cursor-pointer"
              title="Day-ahead wholesale auction gate closure time on D-1"
            >
              <option value={11} className="bg-slate-900 text-white">11:00 UTC (EPEX/NordPool Auction - Recommended)</option>
              <option value={12} className="bg-slate-900 text-white">12:00 UTC (Post-Auction Secondary)</option>
              <option value={17} className="bg-slate-900 text-white">17:00 UTC (Day-Ahead Gate Closure)</option>
              <option value={23} className="bg-slate-900 text-white">23:00 UTC (Final D-1 Nomination)</option>
            </select>
          </div>

          {/* Quick Date Range Picker */}
          <div className="flex items-center gap-1.5 bg-slate-900 border border-slate-800 rounded-lg p-1 text-xs">
            <Calendar className="h-3.5 w-3.5 text-slate-400 ml-1.5 mr-0.5" />
            {quickRanges.map((r) => {
              const isActive = startDate === r.start && endDate === r.end;
              return (
                <button
                  key={r.label}
                  onClick={() => onDateChange(r.start, r.end)}
                  className={`px-2.5 py-1 rounded text-xs transition-colors font-medium ${
                    isActive
                      ? 'bg-cyan-500 text-slate-950 font-semibold shadow-sm'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                  }`}
                >
                  {r.label}
                </button>
              );
            })}
          </div>

          {/* Data Status Pill / Modal Trigger */}
          <button
            onClick={onOpenDataStatus}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-800 bg-slate-900/80 hover:bg-slate-800 text-xs transition-colors"
            title="Inspect Elexon BMRS API and cache status"
          >
            <span className={`h-2 w-2 rounded-full ${dataStatus?.is_cached ? 'bg-emerald-400' : 'bg-cyan-400'} animate-pulse`} />
            <Database className="h-3.5 w-3.5 text-slate-400" />
            <span className="text-slate-300">
              {dataStatus?.is_cached ? 'Real Elexon Cache (100%)' : 'Elexon Live Stream'}
            </span>
          </button>

          {/* Refresh Action */}
          <button
            onClick={onRefresh}
            disabled={isRefreshing}
            className="p-2 rounded-lg border border-slate-800 bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-cyan-400 text-xs transition-colors disabled:opacity-50"
            title="Refresh Elexon Data"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${isRefreshing ? 'animate-spin text-cyan-400' : ''}`} />
          </button>

          {/* CSV Export Action */}
          <a
            href={csvExportUrl}
            download
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-slate-950 font-semibold text-xs transition-colors shadow-sm"
          >
            <Download className="h-3.5 w-3.5" />
            Export CSV
          </a>
        </div>
      </div>
    </header>
  );
};
