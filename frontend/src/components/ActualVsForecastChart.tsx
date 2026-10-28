import React, { useState } from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
  Brush
} from 'recharts';
import { TimeseriesPoint } from '../types';
import { Maximize2, Layers } from 'lucide-react';

interface ChartProps {
  data: TimeseriesPoint[];
  isLoading: boolean;
}

export const ActualVsForecastChart: React.FC<ChartProps> = ({ data, isLoading }) => {
  const [showDifferenceArea, setShowDifferenceArea] = useState(true);

  if (isLoading || !data || data.length === 0) {
    return (
      <div className="h-96 bg-slate-900 border border-slate-800 rounded-xl flex items-center justify-center animate-pulse">
        <span className="text-slate-500 text-sm">Loading time-series data from Elexon...</span>
      </div>
    );
  }

  // Format timestamp for X-axis: "01 Jan 12:00"
  const formattedData = data.map((d) => {
    const dt = new Date(d.startTime);
    const day = dt.getUTCDate().toString().padStart(2, '0');
    const month = dt.toLocaleString('en-GB', { month: 'short' });
    const hours = dt.getUTCHours().toString().padStart(2, '0');
    const mins = dt.getUTCMinutes().toString().padStart(2, '0');
    return {
      ...d,
      formattedTime: `${day} ${month} ${hours}:${mins}`,
      // For Area fill: upper and lower bounds
      maxGen: Math.max(d.actual_mw, d.forecast_mw),
      minGen: Math.min(d.actual_mw, d.forecast_mw),
    };
  });

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const item: TimeseriesPoint = payload[0].payload;
      const signedErr = item.signed_error_mw;
      const isOverForecast = signedErr > 0;

      return (
        <div className="bg-slate-900/95 border border-slate-700 p-3.5 rounded-lg shadow-xl text-xs backdrop-blur font-sans max-w-xs">
          <div className="font-semibold text-slate-200 border-b border-slate-800 pb-1.5 mb-2">
            Delivery: {item.startTime.replace('T', ' ').replace('Z', ' UTC')}
            {item.settlementPeriod ? ` (SP ${item.settlementPeriod})` : ''}
          </div>
          <div className="space-y-1.5">
            <div className="flex justify-between items-center text-emerald-400 font-mono">
              <span className="flex items-center gap-1.5">
                <span className="h-2 w-2 rounded-full bg-emerald-400 inline-block" />
                Actual Wind:
              </span>
              <span className="font-bold">{item.actual_mw.toLocaleString()} MW</span>
            </div>
            <div className="flex justify-between items-center text-cyan-400 font-mono">
              <span className="flex items-center gap-1.5">
                <span className="h-2 w-2 rounded-full bg-cyan-400 inline-block" />
                D-1 Forecast:
              </span>
              <span className="font-bold">{item.forecast_mw.toLocaleString()} MW</span>
            </div>
            <div className="flex justify-between items-center font-mono pt-1 border-t border-slate-800">
              <span className="text-slate-400">Signed Error (F - A):</span>
              <span className={`font-bold ${isOverForecast ? 'text-amber-400' : 'text-blue-400'}`}>
                {signedErr > 0 ? '+' : ''}{signedErr.toLocaleString()} MW
              </span>
            </div>
            <div className="flex justify-between items-center font-mono">
              <span className="text-slate-400">Absolute Error:</span>
              <span className="text-rose-400 font-bold">{item.abs_error_mw.toLocaleString()} MW</span>
            </div>
          </div>
          <div className="mt-2.5 pt-2 border-t border-slate-800/80 text-[10px] text-slate-400">
            <div>Published: {item.publishTime ? item.publishTime.replace('T', ' ').replace('Z', ' UTC') : 'N/A'}</div>
            <div>Cutoff: {item.cutoffTime ? item.cutoffTime.replace('T', ' ').replace('Z', ' UTC') : 'N/A'}</div>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 mb-4">
        <div>
          <h3 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
            <span>National Wind Generation: Actual vs Day-Ahead Forecast</span>
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Hourly WINDFOR forecasts mapped to half-hour FUELHH settlement periods • January 2026
          </p>
        </div>

        {/* Chart View Toggles */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowDifferenceArea(!showDifferenceArea)}
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded text-xs border transition-colors ${
              showDifferenceArea
                ? 'bg-cyan-950 border-cyan-800 text-cyan-300'
                : 'bg-slate-800 border-slate-700 text-slate-400 hover:text-slate-200'
            }`}
          >
            <Layers className="h-3.5 w-3.5" />
            <span>Discrepancy Band</span>
          </button>
        </div>
      </div>

      {/* Chart Canvas */}
      <div className="h-[400px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={formattedData} margin={{ top: 10, right: 20, left: 10, bottom: 25 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis
              dataKey="formattedTime"
              stroke="#64748b"
              tick={{ fill: '#94a3b8', fontSize: 11 }}
              tickLine={{ stroke: '#334155' }}
              minTickGap={45}
            />
            <YAxis
              stroke="#64748b"
              tick={{ fill: '#94a3b8', fontSize: 11 }}
              tickLine={{ stroke: '#334155' }}
              tickFormatter={(v) => `${(v / 1000).toFixed(0)}k MW`}
              domain={[0, 'auto']}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              verticalAlign="top"
              align="right"
              wrapperStyle={{ paddingBottom: '10px', fontSize: '12px' }}
            />

            {/* Difference fill */}
            {showDifferenceArea && (
              <Area
                type="monotone"
                dataKey="maxGen"
                stroke="transparent"
                fill="#38bdf8"
                fillOpacity={0.08}
                name="Forecast Discrepancy"
              />
            )}

            {/* Actual Wind Generation Line */}
            <Line
              type="monotone"
              dataKey="actual_mw"
              name="Actual Wind (FUELHH)"
              stroke="#10b981"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 5, fill: '#10b981' }}
            />

            {/* Day-Ahead Forecast Line */}
            <Line
              type="stepAfter"
              dataKey="forecast_mw"
              name="Day-Ahead Forecast (WINDFOR)"
              stroke="#38bdf8"
              strokeWidth={2}
              strokeDasharray="4 2"
              dot={false}
              activeDot={{ r: 5, fill: '#38bdf8' }}
            />

            {/* Range Brush for smooth pan and zoom */}
            <Brush
              dataKey="formattedTime"
              height={26}
              stroke="#0ea5e9"
              fill="#0f172a"
              tickFormatter={() => ''}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-3 flex flex-wrap items-center justify-between text-xs text-slate-500 pt-2 border-t border-slate-800">
        <div>Use the mini-slider below the chart to zoom into specific storm dates or settlement periods.</div>
        <div>Green line: Actual generation • Blue dashed line: D-1 forecast</div>
      </div>
    </div>
  );
};
