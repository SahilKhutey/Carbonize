import { useState } from 'react';
import { Bell, AlertTriangle, CheckCircle, XCircle, Info } from 'lucide-react';
import { useSimulationStore } from '@/stores/simulationStore';
import { formatRelativeTime } from '@/lib/utils';
import { cn } from '@/lib/utils';

const severityConfig = {
  info: { icon: Info, color: 'sky', bg: 'bg-sky-500/10 border-sky-500/30' },
  warning: { icon: AlertTriangle, color: 'warning', bg: 'bg-warning-500/10 border-warning-500/30' },
  error: { icon: XCircle, color: 'critical', bg: 'bg-critical-500/10 border-critical-500/30' },
  critical: { icon: XCircle, color: 'critical', bg: 'bg-critical-500/20 border-critical-500/50' },
};

export function Alerts() {
  const [filter, setFilter] = useState<'all' | 'unack'>('unack');
  const alerts = useSimulationStore((s) => s.alerts);
  const ackAlert = useSimulationStore((s) => s.acknowledgeAlert);

  const filtered = filter === 'unack' ? alerts.filter((a) => !a.acknowledged) : alerts;

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <Bell className="w-7 h-7 text-carbon-400" />
            Alerts
          </h1>
          <p className="text-slate-400 text-sm mt-1">System notifications and operator actions</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setFilter('unack')}
            className={cn('px-3 py-1.5 text-sm rounded font-medium',
              filter === 'unack' ? 'bg-carbon-500 text-white' : 'bg-slate-800 text-slate-300')}
          >
            Unacknowledged ({alerts.filter((a) => !a.acknowledged).length})
          </button>
          <button
            onClick={() => setFilter('all')}
            className={cn('px-3 py-1.5 text-sm rounded font-medium',
              filter === 'all' ? 'bg-carbon-500 text-white' : 'bg-slate-800 text-slate-300')}
          >
            All
          </button>
        </div>
      </div>

      <div className="space-y-2">
        {filtered.length === 0 ? (
          <div className="text-center py-12 text-slate-500 bg-slate-900 rounded-lg border border-slate-800">
            <CheckCircle className="w-12 h-12 mx-auto opacity-30 mb-3 text-carbon-400" />
            No alerts to display
          </div>
        ) : (
          filtered.map((alert) => {
            const config = severityConfig[alert.severity];
            const Icon = config.icon;
            return (
              <div
                key={alert.id}
                className={cn('rounded-lg p-4 border flex items-start gap-3', config.bg, alert.acknowledged && 'opacity-60')}
              >
                <Icon className={cn('w-5 h-5 flex-shrink-0 mt-0.5',
                  alert.severity === 'critical' ? 'text-critical-400' :
                  alert.severity === 'error' ? 'text-critical-400' :
                  alert.severity === 'warning' ? 'text-warning-400' : 'text-sky-400'
                )} />
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-slate-200">{alert.type.replace('_', ' ').toUpperCase()}</span>
                    <span className="text-xs text-slate-500">{formatRelativeTime(alert.timestamp)}</span>
                  </div>
                  <p className="text-sm text-slate-300 mt-1">{alert.message}</p>
                  {alert.robotId && <p className="text-xs text-slate-500 mt-1">Robot: {alert.robotId}</p>}
                </div>
                {!alert.acknowledged && (
                  <button
                    onClick={() => ackAlert(alert.id)}
                    className="px-3 py-1 text-xs bg-slate-800 text-slate-300 rounded hover:bg-slate-700"
                  >
                    Acknowledge
                  </button>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
