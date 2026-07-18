/**
 * packages/web/src/features/digital-twin/components/ActuatorGrid.tsx
 *
 * Grid of plant actuator controls (ID fan, pumps, ultrasonic).
 * Sends start_equipment / stop_equipment commands via useTwinStream.sendCommand.
 */

import React, { memo, useState, useCallback, useRef, useEffect } from "react";
import { Power, PowerOff, Loader2, AlertCircle } from "lucide-react";
import { TwinState } from "../types/twin";
import { CommandData } from "../../../types/ws";

// ---------------------------------------------------------------------------
// Actuator definitions
// ---------------------------------------------------------------------------

interface ActuatorDef {
  id: string;
  label: string;
  /** Derive ON/OFF from TwinState — pure function */
  isOn: (s: TwinState) => boolean;
  colour: string;
  requiresConfirmation?: boolean;
  warningMessage?: string;
}

const ACTUATORS: ActuatorDef[] = [
  {
    id: "id_fan",
    label: "ID Fan",
    isOn: (s) => s.operating_mode === "running",
    colour: "emerald",
    requiresConfirmation: true,
    warningMessage: "Stopping the ID Fan may cause backpressure in the boiler.",
  },
  {
    id: "reagent_pump_a",
    label: "Reagent Pump A",
    isOn: (s) =>
      s.operating_mode === "running" && (s.current_actuals.flow_nm3_hr ?? 0) > 0,
    colour: "blue",
  },
  {
    id: "reagent_pump_b",
    label: "Reagent Pump B",
    isOn: (s) =>
      s.operating_mode === "running" && (s.current_actuals.reagent_pump_b_flow ?? 0) > 0,
    colour: "blue",
  },
  {
    id: "ultrasonic_1",
    label: "Ultrasonic #1",
    isOn: (s) => (s.current_actuals.mesh_dp_mmH2O ?? 0) > 100,
    colour: "violet",
  },
  {
    id: "hydraulic_press",
    label: "Hydraulic Press",
    isOn: (s) =>
      s.operating_mode === "running" && (s.current_actuals.hydraulic_press_flow ?? 0) > 0,
    colour: "amber",
    requiresConfirmation: true,
  },
];

// ---------------------------------------------------------------------------
// Single actuator button
// ---------------------------------------------------------------------------

interface ActuatorButtonProps {
  def: ActuatorDef;
  isOn: boolean;
  loading: boolean;
  disabled: boolean;
  onToggle: () => void;
}

const ActuatorButton = memo(function ActuatorButton({
  def, isOn, loading, disabled, onToggle,
}: ActuatorButtonProps) {
  const [confirmOpen, setConfirmOpen] = useState(false);
  const buttonRef = useRef<HTMLButtonElement>(null);

  const handleClick = () => {
    if (def.requiresConfirmation) {
      setConfirmOpen(true);
    } else {
      onToggle();
    }
  };

  const confirmAndExecute = () => {
    onToggle();
    setConfirmOpen(false);
    buttonRef.current?.focus();
  };

  const cancelConfirm = () => {
    setConfirmOpen(false);
    buttonRef.current?.focus();
  };
  
  // Close dialog on Escape
  useEffect(() => {
    if (!confirmOpen) return;
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") cancelConfirm();
    };
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [confirmOpen]);

  const borderOn  = `border-${def.colour}-500 bg-${def.colour}-900/40 text-${def.colour}-300`;
  const borderOff = "border-slate-700 bg-slate-800/60 text-slate-400";

  return (
    <>
      <button
        ref={buttonRef}
        id={`actuator-${def.id}`}
        onClick={handleClick}
        disabled={disabled || loading}
        aria-pressed={isOn}
        aria-label={`${def.label}, currently ${isOn ? "on" : "off"}${def.requiresConfirmation ? ", requires confirmation" : ""}`}
        className={`
          relative flex flex-col items-center justify-center p-3 rounded-xl border-2 transition-all duration-200
          min-h-[88px] 
          ${isOn ? borderOn : borderOff}
          ${disabled ? "opacity-40 cursor-not-allowed" : "hover:shadow-md active:scale-95 cursor-pointer"}
          focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2
          focus-visible:outline-emerald-500
        `}
      >
        <div className="flex flex-col items-center gap-1">
          {loading ? (
            <Loader2 className="w-6 h-6 animate-spin" aria-hidden />
          ) : isOn ? (
            <Power className="w-6 h-6" aria-hidden />
          ) : (
            <PowerOff className="w-6 h-6" aria-hidden />
          )}
          <span className="text-sm font-medium truncate">{def.label}</span>
        </div>

        <span
          className={`
            mt-2 inline-block text-xs font-bold px-2 py-0.5 rounded-full
            ${isOn ? `bg-${def.colour}-800 text-${def.colour}-200` : "bg-slate-700 text-slate-500"}
          `}
        >
          {loading ? "…" : isOn ? "ON" : "OFF"}
        </span>
      </button>

      {/* Basic Accessible Modal Dialog */}
      {confirmOpen && (
        <div 
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
          role="dialog"
          aria-modal="true"
          aria-labelledby={`dialog-title-${def.id}`}
          aria-describedby={`dialog-desc-${def.id}`}
        >
          <div 
            className="bg-slate-900 border border-slate-700 rounded-xl p-6 max-w-sm w-full shadow-2xl focus:outline-none"
            tabIndex={-1}
            ref={el => el?.focus()} // auto focus the dialog
          >
            <h2 id={`dialog-title-${def.id}`} className="text-lg font-bold text-white mb-2">
              Confirm: {isOn ? "Stop" : "Start"} {def.label}
            </h2>
            <p id={`dialog-desc-${def.id}`} className="text-sm text-slate-300 mb-6">
              {def.warningMessage ?? `Are you sure you want to ${isOn ? "stop" : "start"} this actuator?`}
            </p>
            <div className="flex justify-end gap-3">
              <button 
                onClick={cancelConfirm}
                className="px-4 py-2 rounded-lg text-sm font-medium border border-slate-600 hover:bg-slate-800 transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-emerald-500"
              >
                Cancel
              </button>
              <button 
                onClick={confirmAndExecute}
                className={`px-4 py-2 rounded-lg text-sm font-medium text-white transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-emerald-500 ${isOn ? 'bg-red-600 hover:bg-red-700' : 'bg-emerald-600 hover:bg-emerald-700'}`}
              >
                Confirm
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
});

// ---------------------------------------------------------------------------
// Grid
// ---------------------------------------------------------------------------

interface ActuatorGridProps {
  state: TwinState;
  onCommand: (cmd: CommandData) => boolean;
  canControl?: boolean;
}

export const ActuatorGrid = memo(function ActuatorGrid({
  state,
  onCommand,
  canControl = false,
}: ActuatorGridProps) {
  const [pending, setPending] = useState<Set<string>>(new Set());

  const handleToggle = useCallback((def: ActuatorDef, currentlyOn: boolean) => {
    const cmd: CommandData = {
      command: currentlyOn ? "stop_equipment" : "start_equipment",
      target: def.id,
    };

    setPending((prev) => new Set(prev).add(def.id));
    const sent = onCommand(cmd);

    // Clear pending after a short timeout (no ack tracking here)
    setTimeout(() => {
      setPending((prev) => {
        const next = new Set(prev);
        next.delete(def.id);
        return next;
      });
    }, sent ? 3000 : 0);
  }, [onCommand]);

  return (
    <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-widest">
          Actuators
        </h3>
        {!canControl && (
          <span className="text-xs text-slate-600 italic">Read-only</span>
        )}
      </div>

      <div 
        className="grid grid-cols-2 sm:grid-cols-3 gap-2 md:gap-3"
        role="group"
        aria-label="Plant actuators"
      >
        {ACTUATORS.map((def) => {
          const isOn = def.isOn(state);
          return (
            <ActuatorButton
              key={def.id}
              def={def}
              isOn={isOn}
              loading={pending.has(def.id)}
              disabled={!canControl}
              onToggle={() => handleToggle(def, isOn)}
            />
          );
        })}
      </div>
    </div>
  );
});
