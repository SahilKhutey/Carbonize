/**
 * packages/web/src/components/layout/AppShell.tsx
 */
import React, { useState } from "react";
import { Outlet, useNavigate } from "react-router-dom";
import { Menu, UserCircle, LogOut } from "lucide-react";
import { Sidebar } from "./Sidebar";
import { useAuth } from "../../hooks/useAuth";

export function AppShell() {
  const [collapsed, setCollapsed] = useState(false);
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="flex h-screen bg-slate-950 text-slate-100 overflow-hidden font-sans">
      {/* Sidebar sidebar transition width */}
      <div 
        className={`transition-all duration-300 ease-in-out shrink-0 ${collapsed ? "w-[72px]" : "w-64"}`}
      >
        <Sidebar collapsed={collapsed} />
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Header */}
        <header className="h-16 border-b border-slate-800 bg-slate-900/50 flex items-center justify-between px-4 shrink-0">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setCollapsed(!collapsed)}
              className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
              aria-label="Toggle Sidebar"
            >
              <Menu className="w-5 h-5" />
            </button>
            <div className="text-sm text-slate-400 font-medium hidden sm:block">
              {/* Breadcrumbs placeholder */}
              CBMS-Sim / <span className="text-slate-200">Dashboard</span>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="text-sm text-right hidden sm:block">
              <p className="font-semibold text-slate-200 leading-tight">{user?.name}</p>
              <p className="text-xs text-slate-500 capitalize">{user?.role}</p>
            </div>
            
            <div className="relative group">
              <button className="flex items-center justify-center w-10 h-10 rounded-full bg-slate-800 border border-slate-700 hover:border-slate-600 transition-colors">
                <UserCircle className="w-6 h-6 text-slate-400 group-hover:text-slate-300" />
              </button>
              
              <div className="absolute right-0 mt-2 w-48 py-2 bg-slate-800 border border-slate-700 rounded-xl shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-50">
                <button 
                  onClick={handleLogout}
                  className="w-full flex items-center gap-2 px-4 py-2 text-sm text-red-400 hover:bg-slate-700/50 transition-colors"
                >
                  <LogOut className="w-4 h-4" />
                  Sign Out
                </button>
              </div>
            </div>
          </div>
        </header>

        {/* Scrollable Page Content */}
        <main className="flex-1 overflow-y-auto p-4 md:p-6 lg:p-8 bg-slate-950">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
