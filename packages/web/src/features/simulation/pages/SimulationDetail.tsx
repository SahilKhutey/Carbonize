/**
 * packages/web/src/features/simulation/pages/SimulationDetail.tsx
 */
import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { AlertCircle, RotateCcw } from "lucide-react";
import { LiveProgressTracker, ProgressState } from "../components/LiveProgressTracker";

export function SimulationDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [status, setStatus] = useState<"RUNNING" | "FAILED" | "COMPLETE">("RUNNING");
  const [progress, setProgress] = useState<ProgressState>({
    stage: "KINETICS",
    percent: 0,
    elapsedTime: "00:00",
  });

  // Mock progress simulation
  useEffect(() => {
    if (status !== "RUNNING") return;

    let time = 0;
    const interval = setInterval(() => {
      time += 1;
      const mins = String(Math.floor(time / 60)).padStart(2, "0");
      const secs = String(time % 60).padStart(2, "0");
      const elapsedTime = `${mins}:${secs}`;

      setProgress((prev) => {
        let newPercent = prev.percent + Math.floor(Math.random() * 5) + 1;
        let newStage = prev.stage;
        let isDone = false;

        if (newPercent >= 100) {
          if (prev.stage === "KINETICS") {
            newStage = "UQ";
            newPercent = 0;
          } else if (prev.stage === "UQ") {
            newStage = "ECONOMICS";
            newPercent = 0;
          } else if (prev.stage === "ECONOMICS") {
            newStage = "REPORT";
            newPercent = 0;
          } else {
            isDone = true;
            newPercent = 100;
          }
        }

        if (isDone) {
          setStatus("COMPLETE");
          clearInterval(interval);
          // Auto-redirect to results after a brief pause
          setTimeout(() => navigate(`/simulations/${id}/results`), 1500);
        }

        return { stage: newStage, percent: newPercent, elapsedTime };
      });
    }, 500);

    return () => clearInterval(interval);
  }, [id, navigate, status]);

  if (status === "FAILED") {
    return (
      <div className="flex h-[80vh] items-center justify-center p-6">
        <div className="max-w-md w-full bg-slate-900 border border-slate-800 p-8 rounded-2xl text-center space-y-4">
          <div className="mx-auto w-16 h-16 bg-red-900/30 text-red-500 rounded-full flex items-center justify-center border border-red-500/30">
            <AlertCircle className="w-8 h-8" />
          </div>
          <h2 className="text-xl font-bold text-white">Simulation Failed</h2>
          <p className="text-slate-400 text-sm">
            The solver encountered a singularity while evaluating the kinetics ODEs at timestep 425.
          </p>
          <button
            onClick={() => setStatus("RUNNING")}
            className="w-full mt-4 flex items-center justify-center gap-2 bg-slate-800 hover:bg-slate-700 text-white py-2.5 rounded-lg transition-colors border border-slate-700"
          >
            <RotateCcw className="w-4 h-4" /> Retry Simulation
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-[80vh] items-center justify-center p-6">
      <LiveProgressTracker progress={progress} />
    </div>
  );
}
