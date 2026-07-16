/**
 * packages/web/src/features/simulation/components/LiveProgressTracker.tsx
 */
import React from "react";
import { CheckCircle2, CircleDashed, Loader2 } from "lucide-react";

export type SimStage = "KINETICS" | "UQ" | "ECONOMICS" | "REPORT";

export interface ProgressState {
  stage: SimStage;
  percent: number;
  elapsedTime: string;
}

const STAGES: { id: SimStage; label: string }[] = [
  { id: "KINETICS", label: "Solving Kinetics" },
  { id: "UQ", label: "Uncertainty Quantification" },
  { id: "ECONOMICS", label: "Economic Analysis" },
  { id: "REPORT", label: "Generating Report" },
];

export function LiveProgressTracker({ progress }: { progress: ProgressState }) {
  const currentStageIndex = STAGES.findIndex((s) => s.id === progress.stage);

  return (
    <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl max-w-2xl w-full">
      <div className="flex justify-between items-end mb-8">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight">Simulation Running</h2>
          <p className="text-sm text-slate-400 mt-1">Please keep this window open.</p>
        </div>
        <div className="text-right">
          <div className="text-2xl font-mono font-light text-emerald-400">{progress.elapsedTime}</div>
          <p className="text-xs text-slate-500 uppercase tracking-widest mt-1">Elapsed</p>
        </div>
      </div>

      <div className="space-y-6">
        {STAGES.map((stage, idx) => {
          const isComplete = idx < currentStageIndex;
          const isCurrent = idx === currentStageIndex;
          const isPending = idx > currentStageIndex;

          return (
            <div key={stage.id} className="relative">
              {/* Connecting line */}
              {idx !== STAGES.length - 1 && (
                <div className={`absolute left-3.5 top-8 w-0.5 h-full -mb-6 ${isComplete ? "bg-emerald-500/50" : "bg-slate-800"}`} />
              )}
              
              <div className="flex items-start gap-4">
                <div className="relative z-10 shrink-0 mt-1">
                  {isComplete && <CheckCircle2 className="w-7 h-7 text-emerald-500 bg-slate-900" />}
                  {isCurrent && <Loader2 className="w-7 h-7 text-emerald-400 animate-spin bg-slate-900" />}
                  {isPending && <CircleDashed className="w-7 h-7 text-slate-600 bg-slate-900" />}
                </div>
                
                <div className={`flex-1 ${isPending ? "opacity-50" : "opacity-100"}`}>
                  <h3 className={`font-semibold ${isCurrent ? "text-emerald-400" : "text-slate-200"}`}>
                    {stage.label}
                  </h3>
                  
                  {isCurrent && (
                    <div className="mt-3 space-y-2">
                      <div className="flex justify-between text-xs text-slate-400">
                        <span>Processing Monte Carlo iterations...</span>
                        <span className="font-mono">{progress.percent}%</span>
                      </div>
                      <div className="h-2 w-full bg-slate-950 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-emerald-500 transition-all duration-300 rounded-full" 
                          style={{ width: `${progress.percent}%` }}
                        />
                      </div>
                    </div>
                  )}
                  
                  {isComplete && (
                    <p className="text-xs text-slate-500 mt-1">Completed successfully.</p>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
