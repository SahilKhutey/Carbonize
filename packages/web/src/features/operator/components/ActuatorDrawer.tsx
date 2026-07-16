/**
 * packages/web/src/features/operator/components/ActuatorDrawer.tsx
 *
 * Pull-up bottom drawer for plant equipment controls.
 * Requires confirmation before any start/stop action.
 * Auditable — every action is sent as a CommandData message via the WS.
 */

import React, { memo, useState, useCallback } from "react";
import { ChevronUp, ChevronDown, Power, PowerOff, Loader2 } from "lucide-react";
import type { TwinState } from "../../digital-twin/types/twin";
import type { CommandData } from "../../../types/ws";
import { ConfirmDialog } from "./ConfirmDialog";

// ---------------------------------------------------------------------------
// Actuator defs
// ---------------------------------------------------------------------------

interface ActuatorDef {
  id: string;
  label: string;
  icon?: string;
  isOn: (s: TwinState) => boolean;
}

const ACTUATORS: ActuatorDef[] = [
  { id: "id_fan",         label: "ID Fan",        icon: "💨", isOn: (s) => s.operating_mode === "running" },
  { id: "reagent_pump_a", label: "Pump A",         icon: "💧", isOn: (s) => (s.current_actuals.flow_nm3_hr ?? 0) > 0 },
  { id: "reagent_pump_b", label: "Pump B",         icon: "💧", isOn: (_) => false },
  { id: "reactor_tower",  label: "Tower",          icon: "🏭", isOn: (s) => s.operating_mode === "running" },
  { id: "ultrasonic_1",   label: "Ultrasonic #1",  icon: "🔊", isOn: (s) => (s.current_actuals.mesh_dp_mmH2O ?? 0) > 100 },
];

// ---------------------------------------------------------------------------
// Button
// ---------------------------------------------------------------------------

interface ActuatorButtonProps {
  def: ActuatorDef;
  state: TwinState;
  loading: boolean;
  disabled: boolean;
  onToggleRequest: (def: ActuatorDef, currentlyOn: boolean) => void;
}

const ActuatorButton = memo(function ActuatorButton({
  def, state, loading, disabled, onToggleRequest,
}: ActuatorButtonProps) {
  const isOn = def.isOn(state);
  return (
    <button
      id={`actuator-${def.id}`}
      onClick={() => onToggleRequest(def, isOn)}
      disabled={disabled || loading}
      aria-pressed={isOn}
      aria-label={`${def.label} ${isOn ? "running — click to stop" : "stopped — click to start"}`}
      className={`
        flex flex-col items-center gap-1
        px-4 py-3 min-w-[80px] min-h-[64px] rounded-xl
        border-2 transition-all duration-150
        ${isOn
          ? "border-emerald-500 bg-emerald-900/40 text-emerald-300"
          : "border-slate-700 bg-slate-800/60 text-slate-400"
        }
        ${disabled ? "opacity-40 cursor-not-allowed" : "hover:brightness-110 cursor-pointer"}
        focus:outline-none focus:ring-2 focus:ring-offset-1 focus:ring-offset-slate-950
        focus:ring-emerald-500
      `}
    >
      <span className="text-lg" aria-hidden>{def.icon}</span>
      {loading ? (
        <Loader2 className="w-4 h-4 animate-spin" aria-hidden />
      ) : isOn ? (
        <Power className="w-4 h-4" aria-hidden />
      ) : (
        <PowerOff className="w-4 h-4" aria-hidden />
      )}
      <span className="text-[10px] font-semibold truncate max-w-full">{def.label}</span>
      <span className={`text-[9px] font-bold ${isOn ? "text-emerald-400" : "text-slate-600"}`}>
        {loading ? "…" : isOn ? "ON" : "OFF"}
      </span>
    </button>
  );
});

// ---------------------------------------------------------------------------
// Drawer
// ---------------------------------------------------------------------------

interface ActuatorDrawerProps {
  state: TwinState;
  onCommand: (cmd: CommandData) => boolean;
  canControl?: boolean;
}

export const ActuatorDrawer = memo(function ActuatorDrawer({
  state,
  onCommand,
  canControl = false,
}: ActuatorDrawerProps) {
  const [open, setOpen] = useState(true);
  const [pending, setPending] = useState<Set<string>>(new Set());
  const [confirmTarget, setConfirmTarget] = useState<{
    def: ActuatorDef;
    currentlyOn: boolean;
  } | null>(null);

  const handleToggleRequest = useCallback((def: ActuatorDef, currentlyOn: boolean) => {
    setConfirmTarget({ def, currentlyOn });
  }, []);

  const handleConfirm = useCallback(() => {
    if (!confirmTarget) return;
    const { def, currentlyOn } = confirmTarget;
    setConfirmTarget(null);
    setPending((p) => new Set(p).add(def.id));
    onCommand({
      command: currentlyOn ? "stop_equipment" : "start_equipment",
      target: def.id,
    });
    setTimeout(() => {
      setPending((p) => { const n = new Set(p); n.delete(def.id); return n; });
    }, 3000);
  }, [confirmTarget, onCommand]);

  return (
    <div
      role="region"
      aria-label="Actuator controls"
      className="border-t border-slate-700 bg-slate-950"
    >
      {/* Pull handle */}
      <button
        onClick={() => setOpen((o) => !o)}
        className="
          w-full flex items-center justify-between
          px-4 py-2 text-xs font-semibold text-slate-400
          hover:text-white hover:bg-slate-800/50 transition-colors
        "
        aria-expanded={open}
        aria-controls="actuator-drawer-content"
      >
        <span>Equipment Controls</span>
        {open ? <ChevronDown className="w-4 h-4" aria-hidden /> : <ChevronUp className="w-4 h-4" aria-hidden />}
      </button>

      {/* Drawer content */}
      {open && (
        <div
          id="actuator-drawer-content"
          className="px-4 pb-4 flex items-end gap-2 overflow-x-auto"
        >
          {!canControl && (
            <p className="text-xs text-slate-600 italic self-center pr-4">
              Read-only mode — operator access required to control equipment
            </p>
          )}
          {ACTUATORS.map((def) => (
            <ActuatorButton
              key={def.id}
              def={def}
              state={state}
              loading={pending.has(def.id)}
              disabled={!canControl}
              onToggleRequest={handleToggleRequest}
            />
          ))}
        </div>
      )}

      {/* Confirmation dialog */}
      {confirmTarget && (
        <ConfirmDialog
          isOpen
          title={`${confirmTarget.currentlyOn ? "Stop" : "Start"} ${confirmTarget.def.label}?`}
          message={
            confirmTarget.currentlyOn
              ? `This will stop the ${confirmTarget.def.label}. Confirm only if you intend to do this.`
              : `This will start the ${confirmTarget.def.label}. Confirm only if safe to do so.`
          }
          confirmLabel={confirmTarget.currentlyOn ? "Stop Equipment" : "Start Equipment"}
          danger={confirmTarget.currentlyOn}
          onConfirm={handleConfirm}
          onCancel={() => setConfirmTarget(null)}
        />
      )}
    </div>
  );
});
