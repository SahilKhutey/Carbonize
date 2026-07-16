/**
 * packages/web/src/features/executive/components/ExecNav.tsx
 *
 * Top navigation bar for the Executive / Report view.
 * 5 nav items, desktop-optimized (mouse targets OK at 32px).
 */

import React, { memo } from "react";
import { NavLink } from "react-router-dom";

const NAV_ITEM =
  "px-4 py-2 rounded-lg text-sm font-medium transition-colors " +
  "text-slate-400 hover:text-white hover:bg-slate-800/60 " +
  "aria-[current=page]:text-emerald-400 aria-[current=page]:bg-slate-800/80";

interface ExecNavProps {
  userName?: string;
}

export const ExecNav = memo(function ExecNav({ userName = "Executive" }: ExecNavProps) {
  return (
    <header
      role="banner"
      className="
        sticky top-0 z-40
        bg-slate-900/95 backdrop-blur
        border-b border-slate-800
        h-14 px-6
        flex items-center justify-between gap-6
      "
    >
      {/* Brand */}
      <div className="flex items-center gap-3 shrink-0">
        <span className="text-emerald-400 font-extrabold text-lg">🌿 CarbonLattice</span>
      </div>

      {/* Nav */}
      <nav aria-label="Executive navigation" className="flex items-center gap-1">
        <NavLink to="/executive/dashboard" className={NAV_ITEM} end>
          Dashboard
        </NavLink>
        <NavLink to="/executive/plants" className={NAV_ITEM}>
          Plants
        </NavLink>
        <NavLink to="/executive/reports" className={NAV_ITEM}>
          Reports
        </NavLink>
        <NavLink to="/executive/analytics" className={NAV_ITEM}>
          Analytics
        </NavLink>
      </nav>

      {/* User */}
      <div className="shrink-0 flex items-center gap-2">
        <span className="text-sm text-slate-400">{userName}</span>
        <div className="w-8 h-8 rounded-full bg-emerald-800 flex items-center justify-center text-xs font-bold text-emerald-200">
          {userName[0].toUpperCase()}
        </div>
      </div>
    </header>
  );
});
