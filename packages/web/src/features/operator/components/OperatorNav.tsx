/**
 * packages/web/src/features/operator/components/OperatorNav.tsx
 *
 * Top navigation bar for the Operator DCS view.
 * 4 items (terse), notification bell, connection status pill.
 */

import React, { memo } from "react";
import { NavLink } from "react-router-dom";
import { Bell, Settings, ChevronDown } from "lucide-react";
import { ConnectionStatus } from "../../digital-twin/components/ConnectionStatus";
import type { ConnectionState } from "../../digital-twin/types/twin";

interface OperatorNavProps {
  plantId?: string;
  alertCount?: number;
  connectionState?: ConnectionState;
  rttMs?: number | null;
  onReconnect?: () => void;
}

const NAV_ITEM =
  "px-3 py-2 rounded-lg text-sm font-medium transition-colors " +
  "text-slate-400 hover:text-white hover:bg-slate-800 " +
  "aria-[current=page]:text-emerald-400 aria-[current=page]:bg-slate-800";

export const OperatorNav = memo(function OperatorNav({
  plantId,
  alertCount = 0,
  connectionState = "disconnected",
  rttMs,
  onReconnect,
}: OperatorNavProps) {
  return (
    <header
      role="banner"
      className="
        fixed top-0 inset-x-0 z-50
        bg-slate-900 border-b border-slate-800
        h-12 px-4
        flex items-center justify-between gap-4
      "
    >
      {/* Brand */}
      <div className="flex items-center gap-3 shrink-0">
        <span className="text-emerald-400 font-extrabold text-lg leading-none">
          🌿 CBMS
        </span>
        <span className="hidden sm:block text-xs text-slate-600">Operator DCS</span>
      </div>

      {/* Nav items */}
      <nav aria-label="Operator navigation" className="flex items-center gap-1">
        <NavLink to="/operator/live" className={NAV_ITEM} end>
          Live Ops
        </NavLink>
        {plantId && (
          <NavLink to={`/operator/schematic/${plantId}`} className={NAV_ITEM}>
            Schematic
          </NavLink>
        )}
        <NavLink to="/operator/alarms" className={NAV_ITEM}>
          Alarms
        </NavLink>
        <NavLink to="/operator/handover" className={NAV_ITEM}>
          Handover
        </NavLink>
      </nav>

      {/* Right cluster */}
      <div className="flex items-center gap-2 shrink-0">
        <ConnectionStatus
          state={connectionState}
          rttMs={rttMs}
          onReconnect={onReconnect}
        />

        {/* Alert bell */}
        <button
          aria-label={`${alertCount} active alerts`}
          className="relative p-2 rounded-lg hover:bg-slate-800 transition-colors"
        >
          <Bell className="w-4 h-4 text-slate-400" aria-hidden />
          {alertCount > 0 && (
            <span
              aria-hidden
              className="
                absolute top-1 right-1 w-4 h-4
                bg-red-500 text-white text-[10px] font-bold
                rounded-full flex items-center justify-center
              "
            >
              {alertCount > 9 ? "9+" : alertCount}
            </span>
          )}
        </button>

        <NavLink
          to="/operator/settings"
          className="p-2 rounded-lg hover:bg-slate-800 transition-colors"
          aria-label="Settings"
        >
          <Settings className="w-4 h-4 text-slate-500" aria-hidden />
        </NavLink>
      </div>
    </header>
  );
});
