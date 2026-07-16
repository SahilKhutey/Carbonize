/**
 * packages/web/src/components/layout/Sidebar.tsx
 */
import React from "react";
import { NavLink } from "react-router-dom";
import { 
  LayoutDashboard, 
  Factory, 
  TestTube, 
  FileText, 
  ShieldCheck, 
  MonitorPlay 
} from "lucide-react";
import { useAuth } from "../../hooks/useAuth";

const NAV_ITEMS = [
  { to: "/dashboard", icon: LayoutDashboard, label: "Dashboard", roles: ["admin", "manager", "engineer"] },
  { to: "/plants", icon: Factory, label: "Plants", roles: ["admin", "manager", "engineer"] },
  { to: "/simulations", icon: TestTube, label: "Simulations", roles: ["admin", "manager", "engineer", "operator"] },
  { to: "/reports", icon: FileText, label: "Reports", roles: ["admin", "manager"] },
  { to: "/compliance", icon: ShieldCheck, label: "Compliance", roles: ["admin", "manager"] },
  { to: "/twin/plant-alpha", icon: MonitorPlay, label: "Digital Twin", roles: ["admin", "manager", "engineer"] },
];

interface SidebarProps {
  collapsed: boolean;
}

export function Sidebar({ collapsed }: SidebarProps) {
  const { hasRole } = useAuth();

  return (
    <div className="flex flex-col h-full bg-slate-900 border-r border-slate-800 text-slate-400">
      <div className="p-4 flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-emerald-900/50 border border-emerald-500/30 flex items-center justify-center shrink-0">
          <Factory className="w-5 h-5 text-emerald-400" />
        </div>
        {!collapsed && (
          <span className="font-bold text-white text-lg tracking-tight">CBMS-Sim</span>
        )}
      </div>

      <nav className="flex-1 overflow-y-auto py-4 space-y-1 px-2">
        {NAV_ITEMS.map((item) => {
          // Hide items the user doesn't have access to
          if (!hasRole(item.roles as any)) return null;

          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) => `
                flex items-center gap-3 px-3 py-2 rounded-lg transition-colors
                ${isActive 
                  ? "bg-emerald-900/30 text-emerald-400 border border-emerald-500/20" 
                  : "hover:bg-slate-800 hover:text-slate-200"
                }
              `}
              title={collapsed ? item.label : undefined}
            >
              <item.icon className="w-5 h-5 shrink-0" />
              {!collapsed && <span className="font-medium text-sm">{item.label}</span>}
            </NavLink>
          );
        })}
      </nav>
    </div>
  );
}
