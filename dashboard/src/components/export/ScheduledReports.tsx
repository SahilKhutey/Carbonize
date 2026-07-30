import { useState } from 'react';
import { Mail, Calendar } from 'lucide-react';
import { Modal } from '@/components/ui/Modal';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';

interface ScheduledReport {
  id: string;
  name: string;
  schedule: 'daily' | 'weekly' | 'monthly';
  recipients: string[];
  format: 'pdf' | 'csv' | 'xlsx';
  enabled: boolean;
}

export function ScheduledReports({ open, onClose }: { open: boolean; onClose: () => void }) {
  const [reports, setReports] = useState<ScheduledReport[]>([
    {
      id: '1',
      name: 'Daily Performance Summary',
      schedule: 'daily',
      recipients: ['team@carbonize.io'],
      format: 'pdf',
      enabled: true,
    },
    {
      id: '2',
      name: 'Weekly Drift & Fairness Audit',
      schedule: 'weekly',
      recipients: ['ml-ops@carbonize.io'],
      format: 'pdf',
      enabled: true,
    },
  ]);
  
  const [newReport, setNewReport] = useState<Partial<ScheduledReport>>({
    name: '',
    schedule: 'daily',
    recipients: [],
    format: 'pdf',
    enabled: true,
  });
  
  return (
    <Modal open={open} onClose={onClose} title="Scheduled Email Reports">
      <div className="space-y-4">
        <div className="space-y-2">
          {reports.map((r) => (
            <div key={r.id} className="bg-surface border border-border rounded-theme-md p-3 flex items-center gap-3">
              <Mail className="w-5 h-5 text-primary-500 flex-shrink-0" />
              <div className="flex-1">
                <div className="font-medium text-text text-sm">{r.name}</div>
                <div className="text-xs text-text-tertiary">
                  {r.schedule.toUpperCase()} • {r.format.toUpperCase()} • {r.recipients.join(', ')}
                </div>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => toast.success(`Test report dispatched to ${r.recipients.join(', ')}`)}
                  className="theme-button text-xs"
                >
                  Test Send
                </button>
                <button
                  onClick={() => setReports(reports.map((x) => x.id === r.id ? { ...x, enabled: !x.enabled } : x))}
                  className={cn('w-9 h-5 rounded-full transition-colors relative', r.enabled ? 'bg-primary-500' : 'bg-border-strong')}
                >
                  <div className={cn('w-4 h-4 rounded-full bg-white transition-transform absolute top-0.5', r.enabled ? 'left-4' : 'left-0.5')} />
                </button>
              </div>
            </div>
          ))}
        </div>
        
        <div className="bg-surface border border-border rounded-theme-md p-4">
          <h3 className="text-sm font-semibold text-text mb-3">Add New Schedule</h3>
          <div className="space-y-3">
            <input
              placeholder="Report Title (e.g. Daily Performance)"
              value={newReport.name}
              onChange={(e) => setNewReport({ ...newReport, name: e.target.value })}
              className="w-full bg-surface-elevated border border-border rounded-theme-md px-3 py-2 text-text text-xs outline-none focus:border-primary-500"
            />
            <div className="grid grid-cols-2 gap-3">
              <select
                value={newReport.schedule}
                onChange={(e) => setNewReport({ ...newReport, schedule: e.target.value as any })}
                className="bg-surface-elevated border border-border rounded-theme-md px-3 py-2 text-text text-xs"
              >
                <option value="daily">Daily Frequency</option>
                <option value="weekly">Weekly Frequency</option>
                <option value="monthly">Monthly Frequency</option>
              </select>
              <select
                value={newReport.format}
                onChange={(e) => setNewReport({ ...newReport, format: e.target.value as any })}
                className="bg-surface-elevated border border-border rounded-theme-md px-3 py-2 text-text text-xs"
              >
                <option value="pdf">PDF Format</option>
                <option value="csv">CSV Format</option>
                <option value="xlsx">Excel Format</option>
              </select>
            </div>
            <input
              placeholder="Recipient email addresses (comma-separated)"
              onChange={(e) => setNewReport({ ...newReport, recipients: e.target.value.split(',').map((s) => s.trim()) })}
              className="w-full bg-surface-elevated border border-border rounded-theme-md px-3 py-2 text-text text-xs outline-none focus:border-primary-500"
            />
            <button
              onClick={() => {
                if (newReport.name && newReport.recipients?.length) {
                  setReports([...reports, { ...newReport, id: Date.now().toString() } as ScheduledReport]);
                  setNewReport({ name: '', schedule: 'daily', recipients: [], format: 'pdf', enabled: true });
                  toast.success('New report schedule created');
                }
              }}
              className="theme-button-primary w-full text-xs font-semibold"
            >
              <Calendar className="w-4 h-4 inline mr-2" />
              Save Schedule
            </button>
          </div>
        </div>
      </div>
    </Modal>
  );
}
