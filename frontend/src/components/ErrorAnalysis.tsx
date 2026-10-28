import React, { useState } from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
  Cell
} from 'recharts';
import { AccuracyResponse } from '../types';
import { AlertTriangle, TrendingDown, Clock, BarChart2 } from 'lucide-react';

interface ErrorAnalysisProps {
  accuracy: AccuracyResponse | null;
  isLoading: boolean;
}

export const ErrorAnalysis: React.FC<ErrorAnalysisProps> = ({ accuracy, isLoading }) => {
  const [activeTab, setActiveTab] = useState<'distribution' | 'daily' | 'hourly' | 'largest'>('distribution');

  if (isLoading || !accuracy) {
    return (
      <div className="h-96 bg-slate-900 border border-slate-800 rounded-xl animate-pulse flex items-center justify-center">
        <span className="text-slate-500 text-sm">Calculating error distribution and analytics...</span>
      </div>
    );
  }

  const { daily_metrics, hourly_profile, error_distribution, largest_errors } = accuracy;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 mb-5">
        <div>
          <h3 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
            <span>Forecast Error & Procurement Risk Analysis</span>
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Statistical bias, error spread, diurnal patterns, and critical dispatch imbalance intervals
          </p>
        </div>

        {/* Tab buttons */}
        <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-lg border border-slate-800 text-xs">
          <button
            onClick={() => setActiveTab('distribution')}
            className={`px-3 py-1.5 rounded-md font-medium transition-colors ${
              activeTab === 'distribution'
                ? 'bg-cyan-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
            }`}
          >
            Distribution
          </button>
          <button
            onClick={() => setActiveTab('daily')}
            className={`px-3 py-1.5 rounded-md font-medium transition-colors ${
              activeTab === 'daily'
                ? 'bg-cyan-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
            }`}
          >
            Daily Accuracy
          </button>
          <button
            onClick={() => setActiveTab('hourly')}
            className={`px-3 py-1.5 rounded-md font-medium transition-colors ${
              activeTab === 'hourly'
                ? 'bg-cyan-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
            }`}
          >
            Diurnal Profile
          </button>
          <button
            onClick={() => setActiveTab('largest')}
            className={`px-3 py-1.5 rounded-md font-medium transition-colors ${
              activeTab === 'largest'
                ? 'bg-cyan-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
            }`}
          >
            Largest Errors ({largest_errors.length})
          </button>
        </div>
      </div>

      {/* Tab 1: Error Distribution Histogram */}
      {activeTab === 'distribution' && (
        <div>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={error_distribution} margin={{ top: 10, right: 20, left: 10, bottom: 40 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis
                  dataKey="bin_range"
                  stroke="#64748b"
                  tick={{ fill: '#94a3b8', fontSize: 10 }}
                  angle={-20}
                  textAnchor="end"
                />
                <YAxis
                  stroke="#64748b"
                  tick={{ fill: '#94a3b8', fontSize: 11 }}
                  tickFormatter={(v) => `${v} SPs`}
                />
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const d = payload[0].payload;
                      return (
                        <div className="bg-slate-900 border border-slate-700 p-2.5 rounded shadow text-xs">
                          <div className="font-semibold text-white">{d.bin_range}</div>
                          <div className="text-cyan-400 font-mono mt-1">Settlement Periods: {d.count}</div>
                          <div className="text-slate-400 text-[10px] mt-0.5">
                            Range: {d.bin_start} MW to {d.bin_end} MW
                          </div>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Bar dataKey="count" name="Frequency (Settlement Periods)">
                  {error_distribution.map((entry, index) => {
                    const isOver = entry.bin_start >= 0;
                    const isAccurate = Math.abs(entry.bin_start) < 1000 && Math.abs(entry.bin_end) <= 1000;
                    let fill = isAccurate ? '#10b981' : isOver ? '#f59e0b' : '#38bdf8';
                    if (entry.bin_start > 3000 || entry.bin_end < -3000) fill = '#f43f5e';
                    return <Cell key={`cell-${index}`} fill={fill} />;
                  })}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
          <p className="text-xs text-slate-400 mt-2 text-center">
            Signed forecast error distribution (Forecast - Actual). Green bars indicate accurate predictions (±500 MW), yellow/orange indicates over-forecasting, rose indicates severe imbalances (&gt;3 GW).
          </p>
        </div>
      )}

      {/* Tab 2: Daily Accuracy Breakdown */}
      {activeTab === 'daily' && (
        <div>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={daily_metrics} margin={{ top: 10, right: 20, left: 10, bottom: 25 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis
                  dataKey="date"
                  stroke="#64748b"
                  tick={{ fill: '#94a3b8', fontSize: 10 }}
                  tickFormatter={(d) => d.slice(8)} // just day of month
                />
                <YAxis
                  stroke="#64748b"
                  tick={{ fill: '#94a3b8', fontSize: 11 }}
                  tickFormatter={(v) => `${(v / 1000).toFixed(0)}k MW`}
                />
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const d = payload[0].payload;
                      return (
                        <div className="bg-slate-900 border border-slate-700 p-2.5 rounded shadow text-xs">
                          <div className="font-semibold text-white">Date: {d.date}</div>
                          <div className="text-cyan-400 font-mono mt-1">MAE: {d.mae_mw} MW</div>
                          <div className="text-blue-400 font-mono">RMSE: {d.rmse_mw} MW</div>
                          <div className="text-amber-400 font-mono">Bias: {d.bias_mw > 0 ? '+' : ''}{d.bias_mw} MW</div>
                          <div className="text-emerald-400 font-mono">WAPE: {d.wape_pct}%</div>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                <Bar dataKey="mae_mw" name="Daily MAE (MW)" fill="#38bdf8" radius={[3, 3, 0, 0]} />
                <Bar dataKey="bias_mw" name="Daily Bias / Mean Error (MW)" fill="#f59e0b" radius={[3, 3, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <p className="text-xs text-slate-400 mt-2 text-center">
            Daily Mean Absolute Error (MAE) and Signed Bias for each day of January 2026.
          </p>
        </div>
      )}

      {/* Tab 3: Hourly Diurnal Profile */}
      {activeTab === 'hourly' && (
        <div>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={hourly_profile} margin={{ top: 10, right: 20, left: 10, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis
                  dataKey="hour"
                  stroke="#64748b"
                  tick={{ fill: '#94a3b8', fontSize: 11 }}
                  tickFormatter={(h) => `${h.toString().padStart(2, '0')}:00`}
                />
                <YAxis
                  stroke="#64748b"
                  tick={{ fill: '#94a3b8', fontSize: 11 }}
                  tickFormatter={(v) => `${(v / 1000).toFixed(0)}k MW`}
                />
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const d = payload[0].payload;
                      return (
                        <div className="bg-slate-900 border border-slate-700 p-2.5 rounded shadow text-xs">
                          <div className="font-semibold text-white">Hour: {d.hour}:00 UTC</div>
                          <div className="text-emerald-400 font-mono mt-1">Avg Actual: {d.avg_actual_mw} MW</div>
                          <div className="text-cyan-400 font-mono">Avg Forecast: {d.avg_forecast_mw} MW</div>
                          <div className="text-rose-400 font-mono">MAE: {d.mae_mw} MW</div>
                          <div className="text-amber-400 font-mono">Bias: {d.bias_mw > 0 ? '+' : ''}{d.bias_mw} MW</div>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                <Line type="monotone" dataKey="avg_actual_mw" name="Avg Actual (MW)" stroke="#10b981" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="avg_forecast_mw" name="Avg Forecast (MW)" stroke="#38bdf8" strokeWidth={2} strokeDasharray="3 3" dot={false} />
                <Line type="monotone" dataKey="mae_mw" name="MAE (MW)" stroke="#fb7185" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <p className="text-xs text-slate-400 mt-2 text-center">
            24-Hour Diurnal Pattern: Average wind output and forecast error across each hour of the day.
          </p>
        </div>
      )}

      {/* Tab 4: Top Largest Error Settlement Intervals */}
      {activeTab === 'largest' && (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-950 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
              <tr>
                <th className="py-2.5 px-3">Delivery UTC</th>
                <th className="py-2.5 px-2">SP</th>
                <th className="py-2.5 px-3 text-right">Actual MW</th>
                <th className="py-2.5 px-3 text-right">Forecast MW</th>
                <th className="py-2.5 px-3 text-right">Signed Error</th>
                <th className="py-2.5 px-3 text-right">Abs Error</th>
                <th className="py-2.5 px-4">Procurement & Commercial Implication</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {largest_errors.map((item, idx) => {
                const isOver = item.signed_error_mw > 0;
                return (
                  <tr key={idx} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-2.5 px-3 whitespace-nowrap text-slate-200">
                      {item.startTime.replace('T', ' ').replace('Z', '')}
                    </td>
                    <td className="py-2.5 px-2 text-slate-400">{item.settlementPeriod || '-'}</td>
                    <td className="py-2.5 px-3 text-right text-emerald-400 font-semibold">
                      {item.actual_mw.toLocaleString()}
                    </td>
                    <td className="py-2.5 px-3 text-right text-cyan-400 font-semibold">
                      {item.forecast_mw.toLocaleString()}
                    </td>
                    <td className={`py-2.5 px-3 text-right font-bold ${isOver ? 'text-amber-400' : 'text-blue-400'}`}>
                      {isOver ? '+' : ''}{item.signed_error_mw.toLocaleString()}
                    </td>
                    <td className="py-2.5 px-3 text-right text-rose-400 font-bold">
                      {item.abs_error_mw.toLocaleString()}
                    </td>
                    <td className="py-2.5 px-4 font-sans text-xs text-slate-300">
                      <span className={`inline-block px-2 py-0.5 rounded text-[10px] font-semibold mr-2 ${
                        isOver ? 'bg-amber-950 text-amber-300 border border-amber-800' : 'bg-blue-950 text-blue-300 border border-blue-800'
                      }`}>
                        {isOver ? 'SURPLUS / OVER-PROCURED' : 'DEFICIT / SHORTAGE'}
                      </span>
                      {item.implication}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
