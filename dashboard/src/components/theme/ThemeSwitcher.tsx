import { useState } from 'react';
import { Moon, Sun, Monitor, Palette, Settings } from 'lucide-react';
import { useTheme } from '@/themes/ThemeProvider';
import { cn } from '@/lib/utils';

export function ThemeSwitcher() {
  const { theme, preferences, setTheme, setMode, availableThemes, customThemes } = useTheme();
  const [open, setOpen] = useState(false);
  
  const allThemes = [...availableThemes, ...customThemes];
  
  return (
    <div className="relative">
      <button
        onClick={() => setOpen(!open)}
        className="p-2 rounded-theme-md hover:bg-surface-hover text-text-secondary hover:text-text transition-colors"
        title="Theme settings"
        aria-label="Theme settings"
      >
        <Palette className="w-5 h-5" />
      </button>
      
      {open && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setOpen(false)} />
          <div className="absolute right-0 top-12 z-50 w-80 bg-surface-elevated border border-border rounded-theme-lg shadow-theme-xl p-4 animate-fade-in">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-text">Theme Settings</h3>
              <button onClick={() => setOpen(false)} className="text-text-tertiary hover:text-text">
                <Settings className="w-4 h-4" />
              </button>
            </div>
            
            <div className="mb-4">
              <label className="text-xs text-text-tertiary uppercase mb-2 block font-semibold">Mode</label>
              <div className="grid grid-cols-3 gap-1 bg-surface rounded-theme-md p-1 border border-border">
                <ModeButton icon={Sun} label="Light" active={preferences.mode === 'light'} onClick={() => setMode('light')} />
                <ModeButton icon={Moon} label="Dark" active={preferences.mode === 'dark'} onClick={() => setMode('dark')} />
                <ModeButton icon={Monitor} label="Auto" active={preferences.mode === 'auto'} onClick={() => setMode('auto')} />
              </div>
            </div>
            
            <div className="mb-4">
              <label className="text-xs text-text-tertiary uppercase mb-2 block font-semibold">Presets</label>
              <div className="space-y-1 max-h-56 overflow-y-auto pr-1">
                {allThemes.map((t) => (
                  <button
                    key={t.id}
                    onClick={() => setTheme(t.id)}
                    className={cn(
                      'w-full flex items-center gap-3 p-2 rounded-theme-md border transition-colors',
                      theme.id === t.id ? 'bg-primary-500/20 border-primary-500/40 text-primary-400' : 'border-transparent hover:bg-surface-hover text-text'
                    )}
                  >
                    <ThemePreview theme={t} />
                    <div className="flex-1 text-left">
                      <div className="text-sm font-medium">{t.name}</div>
                      <div className="text-[11px] text-text-tertiary line-clamp-1">{t.description}</div>
                    </div>
                    {t.custom && <span className="text-[10px] px-1.5 py-0.5 rounded bg-primary-500/20 text-primary-400 font-mono">Custom</span>}
                  </button>
                ))}
              </div>
            </div>
            
            <div className="mb-4">
              <div className="flex justify-between text-xs text-text-tertiary uppercase mb-2 font-semibold">
                <span>Font Scaling</span>
                <span className="font-mono text-text">{(preferences.fontScale * 100).toFixed(0)}%</span>
              </div>
              <input
                type="range"
                min="0.8"
                max="1.5"
                step="0.05"
                value={preferences.fontScale}
                onChange={(e) => useTheme().setFontScale(parseFloat(e.target.value))}
                className="w-full accent-primary-500"
              />
            </div>
            
            <div className="pt-3 border-t border-border">
              <Toggle
                label="Reduced Motion"
                description="Disable non-essential UI animations"
                checked={preferences.motionReduced}
                onChange={useTheme().setMotionReduced}
              />
            </div>
          </div>
        </>
      )}
    </div>
  );
}

function ModeButton({ icon: Icon, label, active, onClick }: any) {
  return (
    <button
      onClick={onClick}
      className={cn(
        'flex items-center justify-center gap-1 px-2 py-1.5 rounded text-xs transition-colors font-medium',
        active ? 'bg-primary-500 text-white' : 'text-text-secondary hover:text-text'
      )}
    >
      <Icon className="w-3.5 h-3.5" />
      {label}
    </button>
  );
}

function ThemePreview({ theme }: { theme: any }) {
  return (
    <div
      className="w-8 h-8 rounded border border-border overflow-hidden flex-shrink-0"
      style={{ background: theme.colors.background }}
    >
      <div className="h-1/2 flex">
        <div className="flex-1" style={{ background: theme.colors.primary[500] }} />
        <div className="flex-1" style={{ background: theme.colors.secondary[500] }} />
      </div>
      <div className="h-1/2" style={{ background: theme.colors.surface }} />
    </div>
  );
}

function Toggle({ label, description, checked, onChange }: any) {
  return (
    <label className="flex items-center justify-between cursor-pointer">
      <div>
        <div className="text-sm font-medium text-text">{label}</div>
        <div className="text-xs text-text-tertiary">{description}</div>
      </div>
      <button
        onClick={() => onChange(!checked)}
        className={cn(
          'w-9 h-5 rounded-full transition-colors relative',
          checked ? 'bg-primary-500' : 'bg-border-strong'
        )}
      >
        <div className={cn(
          'w-4 h-4 rounded-full bg-white transition-transform absolute top-0.5',
          checked ? 'left-4' : 'left-0.5'
        )} />
      </button>
    </label>
  );
}
