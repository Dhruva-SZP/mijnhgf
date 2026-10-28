import React, { useState } from 'react';
import { RecordsResponse } from '../types';
import { Search, ChevronLeft, ChevronRight, ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react';

interface DetailedDataTableProps {
  recordsData: RecordsResponse | null;
  isLoading: boolean;
  page: number;
  pageSize: number;
  sortBy: string;
  sortDesc: boolean;
  search: string;
  onPageChange: (newPage: number) => void;
  onPageSizeChange: (newSize: number) => void;
  onSortChange: (column: string) => void;
  onSearchChange: (search: string) => void;
}

export const DetailedDataTable: React.FC<DetailedDataTableProps> = ({
  recordsData,
  isLoading,
  page,
  pageSize,
  sortBy,
  sortDesc,
  search,
  onPageChange,
  onPageSizeChange,
  onSortChange,
  onSearchChange,
}) => {
  const [searchInput, setSearchInput] = useState(search);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearchChange(searchInput);
  };

  const renderSortIcon = (column: string) => {
    if (sortBy !== column) return <ArrowUpDown className="h-3 w-3 text-slate-600 inline ml-1" />;
    return sortDesc ? (
      <ArrowDown className="h-3 w-3 text-cyan-400 inline ml-1" />
    ) : (
      <ArrowUp className="h-3 w-3 text-cyan-400 inline ml-1" />
    );
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 mb-4">
        <div>
          <h3 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
            <span>Settlement Interval Granular Records</span>
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Full audit log of half-hour settlement periods, actuals, selected day-ahead forecast, and error metrics
          </p>
        </div>

        {/* Search bar & Page Size */}
        <div className="flex flex-wrap items-center gap-2 w-full sm:w-auto">
          <form onSubmit={handleSearchSubmit} className="relative flex-1 sm:w-64">
            <input
              type="text"
              placeholder="Search date, time, run..."
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-8 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500 font-mono"
            />
            <Search className="h-3.5 w-3.5 text-slate-500 absolute left-2.5 top-2" />
          </form>

          <select
            value={pageSize}
            onChange={(e) => onPageSizeChange(Number(e.target.value))}
            className="bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-300 focus:outline-none focus:border-cyan-500"
          >
            <option value={20}>20 / page</option>
            <option value={50}>50 / page</option>
            <option value={100}>100 / page</option>
          </select>
        </div>
      </div>

      {/* Table Container */}
      <div className="overflow-x-auto border border-slate-800/80 rounded-lg">
        <table className="w-full text-left text-xs text-slate-300">
          <thead className="bg-slate-950 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800 select-none">
            <tr>
              <th
                onClick={() => onSortChange('startTime')}
                className="py-3 px-3 cursor-pointer hover:text-cyan-400"
              >
                Delivery Timestamp (UTC) {renderSortIcon('startTime')}
              </th>
              <th className="py-3 px-2">SP</th>
              <th
                onClick={() => onSortChange('actual_mw')}
                className="py-3 px-3 text-right cursor-pointer hover:text-cyan-400"
              >
                Actual (MW) {renderSortIcon('actual_mw')}
              </th>
              <th
                onClick={() => onSortChange('forecast_mw')}
                className="py-3 px-3 text-right cursor-pointer hover:text-cyan-400"
              >
                Selected Forecast (MW) {renderSortIcon('forecast_mw')}
              </th>
              <th
                onClick={() => onSortChange('signed_error_mw')}
                className="py-3 px-3 text-right cursor-pointer hover:text-cyan-400"
              >
                Signed Error {renderSortIcon('signed_error_mw')}
              </th>
              <th
                onClick={() => onSortChange('abs_error_mw')}
                className="py-3 px-3 text-right cursor-pointer hover:text-cyan-400"
              >
                Abs Error {renderSortIcon('abs_error_mw')}
              </th>
              <th className="py-3 px-3">Forecast Published (UTC)</th>
              <th className="py-3 px-3">D-1 Cutoff Applied</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 font-mono">
            {isLoading ? (
              <tr>
                <td colSpan={8} className="py-8 text-center text-slate-500">
                  Loading settlement records...
                </td>
              </tr>
            ) : !recordsData || recordsData.records.length === 0 ? (
              <tr>
                <td colSpan={8} className="py-8 text-center text-slate-500">
                  No settlement records match your filters.
                </td>
              </tr>
            ) : (
              recordsData.records.map((r) => {
                const isOver = r.signed_error_mw > 0;
                return (
                  <tr key={r.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-2 px-3 text-slate-200 whitespace-nowrap">
                      {r.startTime.replace('T', ' ').replace('Z', '')}
                    </td>
                    <td className="py-2 px-2 text-slate-400">{r.settlementPeriod || '-'}</td>
                    <td className="py-2 px-3 text-right text-emerald-400 font-semibold">
                      {r.actual_mw.toLocaleString()}
                    </td>
                    <td className="py-2 px-3 text-right text-cyan-400 font-semibold">
                      {r.forecast_mw.toLocaleString()}
                    </td>
                    <td className={`py-2 px-3 text-right font-bold ${isOver ? 'text-amber-400' : 'text-blue-400'}`}>
                      {isOver ? '+' : ''}{r.signed_error_mw.toLocaleString()}
                    </td>
                    <td className="py-2 px-3 text-right text-rose-400 font-bold">
                      {r.abs_error_mw.toLocaleString()}
                    </td>
                    <td className="py-2 px-3 text-slate-400 text-[11px] whitespace-nowrap">
                      {r.publishTime ? r.publishTime.replace('T', ' ').replace('Z', '') : '-'}
                    </td>
                    <td className="py-2 px-3 text-slate-500 text-[11px] whitespace-nowrap">
                      {r.cutoffTime ? r.cutoffTime.replace('T', ' ').replace('Z', '') : '-'}
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination Footer */}
      {recordsData && recordsData.total_pages > 1 && (
        <div className="flex flex-col sm:flex-row items-center justify-between gap-3 mt-4 text-xs text-slate-400">
          <div>
            Showing {(page - 1) * pageSize + 1} to{' '}
            {Math.min(page * pageSize, recordsData.total_records)} of{' '}
            {recordsData.total_records.toLocaleString()} intervals
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => onPageChange(page - 1)}
              disabled={page <= 1}
              className="flex items-center gap-1 px-3 py-1.5 rounded border border-slate-800 bg-slate-950 text-slate-300 hover:bg-slate-800 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronLeft className="h-3.5 w-3.5" />
              <span>Previous</span>
            </button>

            <span className="font-mono text-slate-300 px-2">
              Page {page} of {recordsData.total_pages}
            </span>

            <button
              onClick={() => onPageChange(page + 1)}
              disabled={page >= recordsData.total_pages}
              className="flex items-center gap-1 px-3 py-1.5 rounded border border-slate-800 bg-slate-950 text-slate-300 hover:bg-slate-800 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              <span>Next</span>
              <ChevronRight className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
