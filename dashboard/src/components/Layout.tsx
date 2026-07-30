import { useState } from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import {
  Activity,
  Box,
  Play,
  ScanLine,
  Brain,
  BarChart3,
  Bot,
  Bell,
  FlaskConical,
  Palette,
  ChevronLeft,
  ChevronRight,
  LineChart,
  Cpu,
  TestTube,
  Layers,
  TrendingUp,
  Radio,
  Trophy,
  Atom,
} from 'lucide-react';
import { ConnectionIndicator } from './ConnectionIndicator';
import { ThemeSwitcher } from './theme/ThemeSwitcher';
import { cn } from '@/lib/utils';

const navItems = [
  { to: '/', label: 'Overview', icon: Activity },
  { to: '/scene', label: '3D Scene', icon: Box },
  { to: '/simulation', label: 'Simulation', icon: Play },
  { to: '/chemistry', label: 'Core Chemistry', icon: Atom },
  { to: '/reactor', label: 'Reactor Modeling', icon: Cpu },
  { to: '/lab', label: 'Chemistry Lab', icon: FlaskConical },
  { to: '/compchem', label: 'Comp Chem', icon: Brain },
  { to: '/detections', label: 'Detections', icon: ScanLine },
  { to: '/models', label: 'Model Registry', icon: Brain },
  { to: '/ml-analytics', label: 'ML Analytics', icon: Cpu },
  { to: '/test/single', label: 'Single Test', icon: TestTube },
  { to: '/test/batch', label: 'Batch/AB Test', icon: Layers },
  { to: '/predictive', label: 'Predictive AI', icon: TrendingUp },
  { to: '/streaming', label: 'Streaming AI', icon: Radio },
  { to: '/drift', label: 'Stream Drift', icon: Activity },
  { to: '/anomaly', label: 'Anomaly AI', icon: Brain },
  { to: '/gameday', label: 'Game Days', icon: Trophy },
  { to: '/analytics', label: 'Analytics', icon: BarChart3 },
  { to: '/advanced-analytics', label: 'Adv. Analytics', icon: LineChart },
  { to: '/fleet', label: 'Robot Fleet', icon: Bot },
  { to: '/alerts', label: 'Alerts', icon: Bell },
  { to: '/experiments', label: 'A/B Tests', icon: FlaskConical },
  { to: '/theme-customizer', label: 'Themes', icon: Palette },
];

export function Layout() {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <div className="flex h-screen bg-bg text-text overflow-hidden transition-colors">
      <aside
        className={cn(
          'flex flex-col border-r border-border bg-surface transition-all duration-300 z-20',
          collapsed ? 'w-16' : 'w-64'
        )}
      >
        <div className="flex items-center justify-between p-4 border-b border-border">
          {!collapsed && (
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded bg-primary-500 flex items-center justify-center font-bold text-white shadow-theme-glow text-sm">
                C
              </div>
              <span className="font-bold text-lg text-text">Carbonize</span>
            </div>
          )}
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="p-1 rounded text-text-tertiary hover:text-text hover:bg-surface-hover transition-colors"
          >
            {collapsed ? <ChevronRight className="w-5 h-5" /> : <ChevronLeft className="w-5 h-5" />}
          </button>
        </div>

        <nav className="flex-1 overflow-y-auto p-2 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === '/'}
                className={({ isActive }) =>
                  cn(
                    'flex items-center gap-3 px-3 py-2 rounded-theme-md text-sm transition-colors',
                    isActive
                      ? 'bg-primary-500/20 text-primary-400 font-semibold border border-primary-500/30'
                      : 'text-text-secondary hover:text-text hover:bg-surface-hover'
                  )
                }
              >
                <Icon className="w-5 h-5 flex-shrink-0" />
                {!collapsed && <span>{item.label}</span>}
              </NavLink>
            );
          })}
        </nav>

        <div className="p-4 border-t border-border flex items-center justify-between text-xs text-text-tertiary">
          {!collapsed && <span>System v2.5</span>}
          <ConnectionIndicator />
        </div>
      </aside>

      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <header className="h-14 border-b border-border bg-surface px-6 flex items-center justify-between">
          <div className="text-sm font-medium text-text-secondary">
            Autonomous CO₂ Capture Infrastructure Platform
          </div>
          <div className="flex items-center gap-3">
            <ThemeSwitcher />
          </div>
        </header>

        <main className="flex-1 overflow-y-auto bg-bg">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
