import React from 'react';
import { PublicationHistoryResponse } from '../types';
import { ShieldCheck, Clock, FileText, CheckCircle2, ArrowRight } from 'lucide-react';

interface PublicationHistoryProps {
  history: PublicationHistoryResponse | null;
  isLoading: boolean;
}

export const PublicationHistory: React.FC<PublicationHistoryProps> = ({ history, isLoading }) => {
  if (isLoading || !history) {
    return (
      <div className="h-64 bg-slate-900 border border-slate-800 rounded-xl animate-pulse flex items-center justify-center">
        <span className="text-slate-500 text-sm">Loading publication audit trail...</span>
      </div>
    );
  }

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 mb-4">
        <div>
          <h3 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
            <ShieldCheck className="h-5 w-5 text-emerald-400" />
            <span>Forecast Publication Audit & Leakage Prevention</span>
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Verification of forecast publication timestamps against the day-ahead procurement cutoff
          </p>
        </div>

        <div className="flex items-center gap-2 bg-emerald-950/40 border border-emerald-800/60 px-3 py-1.5 rounded-lg text-xs font-mono text-emerald-400">
          <CheckCircle2 className="h-4 w-4" />
          <span>{history.leakage_prevented_count.toLocaleString()} Future Forecasts Excluded (Zero Leakage)</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* Methodology & Policy Rules */}
        <div className="lg:col-span-1 bg-slate-950/70 border border-slate-800/80 rounded-lg p-4 text-xs">
          <h4 className="font-semibold text-slate-200 mb-2.5 flex items-center gap-1.5">
            <Clock className="h-4 w-4 text-cyan-400" />
            <span>Procurement Decision Policy</span>
          </h4>
          <div className="space-y-2 text-slate-300">
            <div className="p-2.5 rounded bg-slate-900 border border-slate-800">
              <span className="text-slate-400 block text-[10px] uppercase font-mono">Market Gate Closure</span>
              <span className="font-semibold text-white">
                Day D-1 at {history.decision_cutoff_hour.toString().padStart(2, '0')}:00 UTC
              </span>
            </div>
            <div className="p-2.5 rounded bg-slate-900 border border-slate-800">
              <span className="text-slate-400 block text-[10px] uppercase font-mono">Selection Algorithm</span>
              <span className="font-medium text-slate-200">
                Latest WINDFOR run with publishTime &le; (D-1) Cutoff
              </span>
            </div>
            <div className="p-2.5 rounded bg-slate-900 border border-slate-800">
              <span className="text-slate-400 block text-[10px] uppercase font-mono">Audit Result</span>
              <span className="font-medium text-emerald-400">
                100% of matched intervals respect historical availability
              </span>
            </div>
          </div>
        </div>

        {/* Selected Publication Runs Breakdown */}
        <div className="lg:col-span-2 bg-slate-950/70 border border-slate-800/80 rounded-lg p-4 text-xs">
          <h4 className="font-semibold text-slate-200 mb-2.5 flex items-center gap-1.5">
            <FileText className="h-4 w-4 text-cyan-400" />
            <span>Primary Publication Versions Selected</span>
          </h4>
          <div className="space-y-2">
            {history.versions.slice(0, 5).map((v, i) => (
              <div key={i} className="flex items-center justify-between p-2 rounded bg-slate-900 border border-slate-800/80">
                <div className="flex items-center gap-2">
                  <span className="h-2 w-2 rounded-full bg-cyan-400" />
                  <span className="font-mono text-slate-200">{v.publishTime.replace('T', ' ').replace('Z', ' UTC')}</span>
                  <span className="text-slate-400">({v.description})</span>
                </div>
                <div className="flex items-center gap-3 font-mono">
                  <span className="text-slate-300">{v.count} intervals</span>
                  <span className="px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 font-semibold border border-cyan-800/50">
                    {v.percentage}%
                  </span>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-3 text-[11px] text-slate-400 flex items-start gap-1.5">
            <ArrowRight className="h-3.5 w-3.5 text-cyan-400 shrink-0 mt-0.5" />
            <span>
              National Grid ESO issues WINDFOR runs periodically (02:30, 04:30, 07:30, 09:30, 11:30, etc.). When cutoff is 11:00 UTC, the 09:30 UTC publication run serves as the primary day-ahead forecast baseline.
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
