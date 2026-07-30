import { useState } from 'react';
import { Save, Download, Upload, RotateCcw } from 'lucide-react';
import { useTheme } from '@/themes/ThemeProvider';
import { defaultDarkTheme } from '@/themes/definitions';
import type { Theme, ColorScale } from '@/themes/types';
import { cn } from '@/lib/utils';

export function ThemeCustomizer() {
  const { theme, applyCustomTheme } = useTheme();
  const [editingTheme, setEditingTheme] = useState<Theme>(() => cloneTheme(theme));
  const [activeSection, setActiveSection] = useState('primary');
  
  function cloneTheme(t: Theme): Theme {
    return JSON.parse(JSON.stringify(t));
  }
  
  const updateColor = (scale: keyof Theme['colors'], key: keyof ColorScale, value: string) => {
    setEditingTheme((prev) => {
      const scaleObj = prev.colors[scale] as any;
      return {
        ...prev,
        colors: {
          ...prev.colors,
          [scale]: { ...scaleObj, [key]: value },
        },
      };
    });
  };
  
  const updateSurface = (key: keyof Theme['colors'], value: string) => {
    setEditingTheme((prev) => ({
      ...prev,
      colors: { ...prev.colors, [key]: value },
    }));
  };
  
  const applyChanges = () => {
    applyCustomTheme(editingTheme);
  };
  
  const exportTheme = () => {
    const blob = new Blob([JSON.stringify(editingTheme, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${editingTheme.id}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };
  
  const importTheme = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const imported = JSON.parse(e.target?.result as string) as Theme;
        setEditingTheme(imported);
      } catch (err) {
        console.error('Failed to import theme:', err);
      }
    };
    reader.readAsText(file);
  };
  
  const reset = () => {
    setEditingTheme(cloneTheme(defaultDarkTheme));
  };
  
  return (
    <div className="p-6 space-y-4 h-full">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text">Theme Customizer</h1>
          <p className="text-text-secondary text-sm mt-1">Design and save custom UI color palettes</p>
        </div>
      </div>

      <div className="grid grid-cols-12 gap-4 h-[calc(100vh-180px)]">
        <div className="col-span-2 bg-surface border border-border rounded-theme-lg p-2 space-y-1">
          <SectionButton active={activeSection === 'primary'} onClick={() => setActiveSection('primary')}>Primary</SectionButton>
          <SectionButton active={activeSection === 'secondary'} onClick={() => setActiveSection('secondary')}>Secondary</SectionButton>
          <SectionButton active={activeSection === 'surfaces'} onClick={() => setActiveSection('surfaces')}>Surfaces</SectionButton>
          <SectionButton active={activeSection === 'text'} onClick={() => setActiveSection('text')}>Text</SectionButton>
          <SectionButton active={activeSection === 'borders'} onClick={() => setActiveSection('borders')}>Borders</SectionButton>
          <SectionButton active={activeSection === 'semantic'} onClick={() => setActiveSection('semantic')}>Semantic</SectionButton>
          <SectionButton active={activeSection === 'charts'} onClick={() => setActiveSection('charts')}>Charts</SectionButton>
          <SectionButton active={activeSection === 'scene'} onClick={() => setActiveSection('scene')}>3D Scene</SectionButton>
        </div>
        
        <div className="col-span-7 bg-surface border border-border rounded-theme-lg p-4 overflow-y-auto">
          <div className="flex items-center justify-between mb-4 pb-3 border-b border-border">
            <input
              value={editingTheme.name}
              onChange={(e) => setEditingTheme({ ...editingTheme, name: e.target.value })}
              className="bg-transparent text-lg font-semibold text-text border-b border-border focus:border-primary-500 outline-none px-1"
            />
            <div className="flex gap-2">
              <button onClick={reset} className="theme-button flex items-center gap-1 text-xs">
                <RotateCcw className="w-3.5 h-3.5" /> Reset
              </button>
              <label className="theme-button flex items-center gap-1 text-xs cursor-pointer">
                <Upload className="w-3.5 h-3.5" /> Import
                <input type="file" accept=".json" onChange={importTheme} className="hidden" />
              </label>
              <button onClick={exportTheme} className="theme-button flex items-center gap-1 text-xs">
                <Download className="w-3.5 h-3.5" /> Export
              </button>
              <button onClick={applyChanges} className="theme-button-primary flex items-center gap-1 text-xs font-semibold">
                <Save className="w-3.5 h-3.5" /> Apply Theme
              </button>
            </div>
          </div>
          
          {activeSection === 'primary' && (
            <ColorScaleEditor
              name="Primary"
              scale={editingTheme.colors.primary}
              onChange={(key, value) => updateColor('primary', key as any, value)}
            />
          )}
          {activeSection === 'secondary' && (
            <ColorScaleEditor
              name="Secondary"
              scale={editingTheme.colors.secondary}
              onChange={(key, value) => updateColor('secondary', key as any, value)}
            />
          )}
          {activeSection === 'surfaces' && (
            <div className="space-y-3">
              <ColorInput label="Background" value={editingTheme.colors.background} onChange={(v) => updateSurface('background', v)} />
              <ColorInput label="Surface" value={editingTheme.colors.surface} onChange={(v) => updateSurface('surface', v)} />
              <ColorInput label="Surface Elevated" value={editingTheme.colors.surfaceElevated} onChange={(v) => updateSurface('surfaceElevated', v)} />
              <ColorInput label="Surface Hover" value={editingTheme.colors.surfaceHover} onChange={(v) => updateSurface('surfaceHover', v)} />
              <ColorInput label="Surface Active" value={editingTheme.colors.surfaceActive} onChange={(v) => updateSurface('surfaceActive', v)} />
            </div>
          )}
          {activeSection === 'text' && (
            <div className="space-y-3">
              <ColorInput label="Text Primary" value={editingTheme.colors.textPrimary} onChange={(v) => updateSurface('textPrimary', v)} />
              <ColorInput label="Text Secondary" value={editingTheme.colors.textSecondary} onChange={(v) => updateSurface('textSecondary', v)} />
              <ColorInput label="Text Tertiary" value={editingTheme.colors.textTertiary} onChange={(v) => updateSurface('textTertiary', v)} />
              <ColorInput label="Text Disabled" value={editingTheme.colors.textDisabled} onChange={(v) => updateSurface('textDisabled', v)} />
            </div>
          )}
          {activeSection === 'borders' && (
            <div className="space-y-3">
              <ColorInput label="Border" value={editingTheme.colors.border} onChange={(v) => updateSurface('border', v)} />
              <ColorInput label="Border Muted" value={editingTheme.colors.borderMuted} onChange={(v) => updateSurface('borderMuted', v)} />
              <ColorInput label="Border Strong" value={editingTheme.colors.borderStrong} onChange={(v) => updateSurface('borderStrong', v)} />
              <ColorInput label="Border Focus" value={editingTheme.colors.borderFocus} onChange={(v) => updateSurface('borderFocus', v)} />
            </div>
          )}
          {activeSection === 'semantic' && (
            <div className="space-y-3">
              <ColorInput label="Success" value={editingTheme.colors.success[500]} onChange={(v) => updateColor('success', 500, v)} />
              <ColorInput label="Warning" value={editingTheme.colors.warning[500]} onChange={(v) => updateColor('warning', 500, v)} />
              <ColorInput label="Danger" value={editingTheme.colors.danger[500]} onChange={(v) => updateColor('danger', 500, v)} />
              <ColorInput label="Info" value={editingTheme.colors.info[500]} onChange={(v) => updateColor('info', 500, v)} />
            </div>
          )}
          {activeSection === 'charts' && (
            <div className="grid grid-cols-2 gap-3">
              {Array.from({ length: 8 }, (_, i) => (
                <ColorInput
                  key={i}
                  label={`Chart ${i + 1}`}
                  value={(editingTheme.colors as any)[`chart${i + 1}`]}
                  onChange={(v) => setEditingTheme((prev) => ({
                    ...prev,
                    colors: { ...prev.colors, [`chart${i + 1}`]: v } as any,
                  }))}
                />
              ))}
            </div>
          )}
          {activeSection === 'scene' && (
            <div className="space-y-3">
              <ColorInput label="Scene Sky" value={editingTheme.colors.sceneSky} onChange={(v) => updateSurface('sceneSky', v)} />
              <ColorInput label="Scene Ground" value={editingTheme.colors.sceneGround} onChange={(v) => updateSurface('sceneGround', v)} />
              <ColorInput label="Scene Grid" value={editingTheme.colors.sceneGrid} onChange={(v) => updateSurface('sceneGrid', v)} />
              <ColorInput label="Robot Color" value={editingTheme.colors.sceneRobot} onChange={(v) => updateSurface('sceneRobot', v)} />
              <ColorInput label="Path Color" value={editingTheme.colors.scenePath} onChange={(v) => updateSurface('scenePath', v)} />
              <ColorInput label="Detection Color" value={editingTheme.colors.sceneDetection} onChange={(v) => updateSurface('sceneDetection', v)} />
            </div>
          )}
        </div>
        
        <div className="col-span-3 bg-surface border border-border rounded-theme-lg p-4 overflow-y-auto">
          <h3 className="font-semibold text-text mb-3">Live Preview</h3>
          <PreviewCard theme={editingTheme} />
        </div>
      </div>
    </div>
  );
}

function SectionButton({ children, active, onClick }: any) {
  return (
    <button
      onClick={onClick}
      className={cn(
        'w-full text-left px-3 py-2 rounded-theme-md text-sm font-medium transition-colors',
        active ? 'bg-primary-500/20 text-primary-400 border border-primary-500/30' : 'text-text-secondary hover:bg-surface-hover'
      )}
    >
      {children}
    </button>
  );
}

function ColorScaleEditor({ name, scale, onChange }: { name: string; scale: any; onChange: (key: string, value: string) => void }) {
  return (
    <div>
      <h3 className="font-semibold text-text mb-3">{name} Color Scale</h3>
      <div className="space-y-3">
        {Object.entries(scale).map(([key, value]) => (
          <ColorInput key={key} label={`${name} ${key}`} value={value as string} onChange={(v) => onChange(key, v)} />
        ))}
      </div>
    </div>
  );
}

function ColorInput({ label, value, onChange }: { label: string; value: string; onChange: (v: string) => void }) {
  return (
    <div className="flex items-center gap-3">
      <input
        type="color"
        value={value || '#000000'}
        onChange={(e) => onChange(e.target.value)}
        className="w-10 h-10 rounded-theme-md border border-border cursor-pointer bg-transparent"
      />
      <div className="flex-1">
        <div className="text-xs text-text-secondary font-medium">{label}</div>
        <input
          type="text"
          value={value || ''}
          onChange={(e) => onChange(e.target.value)}
          className="text-xs text-text-tertiary font-mono bg-transparent border-b border-border focus:border-primary-500 outline-none w-full"
        />
      </div>
    </div>
  );
}

function PreviewCard({ theme }: { theme: Theme }) {
  return (
    <div className="space-y-3">
      <div className="p-3 rounded-theme-md" style={{ background: theme.colors.surface, border: `1px solid ${theme.colors.border}` }}>
        <div className="text-sm font-semibold" style={{ color: theme.colors.textPrimary }}>Sample Card</div>
        <div className="text-xs mt-1" style={{ color: theme.colors.textSecondary }}>This is secondary text</div>
        <div className="text-xs mt-1" style={{ color: theme.colors.textTertiary }}>This is tertiary text</div>
      </div>
      <div className="flex gap-2">
        <button
          className="px-3 py-1.5 rounded-theme-md text-xs font-medium"
          style={{ background: theme.colors.primary[500], color: '#ffffff' }}
        >
          Primary
        </button>
        <button
          className="px-3 py-1.5 rounded-theme-md text-xs font-medium"
          style={{ background: theme.colors.secondary[500], color: '#ffffff' }}
        >
          Secondary
        </button>
      </div>
      <div className="h-10 rounded-theme-md flex overflow-hidden border border-border">
        {Array.from({ length: 8 }, (_, i) => (
          <div key={i} className="flex-1" style={{ background: (theme.colors as any)[`chart${i + 1}`] }} />
        ))}
      </div>
    </div>
  );
}
