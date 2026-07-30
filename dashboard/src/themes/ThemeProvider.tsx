import React, { createContext, useContext, useEffect, useState, useCallback, useMemo } from 'react';
import type { Theme, ThemeName, ThemeMode, ThemePreferences } from './types';
import { builtInThemes, themesById, defaultDarkTheme } from './definitions';

interface ThemeContextValue {
  theme: Theme;
  preferences: ThemePreferences;
  setTheme: (id: ThemeName) => void;
  setMode: (mode: ThemeMode) => void;
  setFontScale: (scale: number) => void;
  setMotionReduced: (reduced: boolean) => void;
  applyCustomTheme: (theme: Theme) => void;
  resetToDefault: () => void;
  availableThemes: Theme[];
  customThemes: Theme[];
}

const ThemeContext = createContext<ThemeContextValue | undefined>(undefined);

const STORAGE_KEY = 'carbonize-theme-prefs';
const CUSTOM_THEMES_KEY = 'carbonize-custom-themes';

const DEFAULT_PREFS: ThemePreferences = {
  theme: 'default-dark',
  mode: 'dark',
  fontScale: 1.0,
  motionReduced: false,
  highContrast: false,
};

interface ThemeProviderProps {
  children: React.ReactNode;
  defaultPreferences?: Partial<ThemePreferences>;
}

export function ThemeProvider({ children, defaultPreferences }: ThemeProviderProps) {
  const [preferences, setPreferences] = useState<ThemePreferences>(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored ? { ...DEFAULT_PREFS, ...JSON.parse(stored), ...defaultPreferences } : { ...DEFAULT_PREFS, ...defaultPreferences };
  });
  
  const [customThemes, setCustomThemes] = useState<Theme[]>(() => {
    const stored = localStorage.getItem(CUSTOM_THEMES_KEY);
    return stored ? JSON.parse(stored) : [];
  });
  
  const [systemMode, setSystemMode] = useState<'dark' | 'light'>(() => 
    typeof window !== 'undefined' && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  );
  
  const activeTheme = useMemo<Theme>(() => {
    const effectiveMode = preferences.mode === 'auto' ? systemMode : preferences.mode;
    
    const custom = customThemes.find((t) => t.id === preferences.theme);
    if (custom) return custom;
    
    const builtIn = themesById(preferences.theme);
    if (builtIn) {
      if (builtIn.mode !== effectiveMode && !builtIn.custom) {
        const equivalent = builtInThemes.find((t) => 
          t.id.startsWith('default') && t.mode === effectiveMode
        );
        return equivalent || builtIn;
      }
      return builtIn;
    }
    
    return defaultDarkTheme;
  }, [preferences, systemMode, customThemes]);
  
  useEffect(() => {
    const root = document.documentElement;
    
    const cssVars = themeToCSSVariables(activeTheme);
    Object.entries(cssVars).forEach(([key, value]) => {
      root.style.setProperty(key, value);
    });
    
    root.classList.remove('dark', 'light');
    root.classList.add(activeTheme.mode);
    root.setAttribute('data-theme', activeTheme.mode);
    
    root.style.fontSize = `${preferences.fontScale * 16}px`;
    
    if (preferences.motionReduced) {
      root.classList.add('reduce-motion');
    } else {
      root.classList.remove('reduce-motion');
    }
  }, [activeTheme, preferences.fontScale, preferences.motionReduced]);
  
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handler = (e: MediaQueryListEvent) => setSystemMode(e.matches ? 'dark' : 'light');
    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, []);
  
  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(preferences));
  }, [preferences]);
  
  useEffect(() => {
    localStorage.setItem(CUSTOM_THEMES_KEY, JSON.stringify(customThemes));
  }, [customThemes]);
  
  const setTheme = useCallback((id: ThemeName) => {
    setPreferences((p) => ({ ...p, theme: id }));
  }, []);
  
  const setMode = useCallback((mode: ThemeMode) => {
    setPreferences((p) => ({ ...p, mode }));
  }, []);
  
  const setFontScale = useCallback((scale: number) => {
    setPreferences((p) => ({ ...p, fontScale: Math.max(0.8, Math.min(1.5, scale)) }));
  }, []);
  
  const setMotionReduced = useCallback((reduced: boolean) => {
    setPreferences((p) => ({ ...p, motionReduced: reduced }));
  }, []);
  
  const applyCustomTheme = useCallback((theme: Theme) => {
    setCustomThemes((themes) => {
      const existing = themes.findIndex((t) => t.id === theme.id);
      if (existing >= 0) {
        const updated = [...themes];
        updated[existing] = { ...theme, custom: true };
        return updated;
      }
      return [...themes, { ...theme, custom: true }];
    });
    setPreferences((p) => ({ ...p, theme: theme.id }));
  }, []);
  
  const resetToDefault = useCallback(() => {
    setPreferences(DEFAULT_PREFS);
    setCustomThemes([]);
  }, []);
  
  const value: ThemeContextValue = {
    theme: activeTheme,
    preferences,
    setTheme,
    setMode,
    setFontScale,
    setMotionReduced,
    applyCustomTheme,
    resetToDefault,
    availableThemes: builtInThemes,
    customThemes,
  };
  
  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) throw new Error('useTheme must be used within ThemeProvider');
  return context;
}

function themeToCSSVariables(theme: Theme): Record<string, string> {
  const vars: Record<string, string> = {};
  
  Object.entries(theme.colors.primary).forEach(([key, value]) => {
    vars[`--color-primary-${key}`] = value as string;
  });
  
  vars['--color-bg'] = theme.colors.background;
  vars['--color-surface'] = theme.colors.surface;
  vars['--color-surface-elevated'] = theme.colors.surfaceElevated;
  vars['--color-surface-hover'] = theme.colors.surfaceHover;
  vars['--color-surface-active'] = theme.colors.surfaceActive;
  
  vars['--color-text'] = theme.colors.textPrimary;
  vars['--color-text-secondary'] = theme.colors.textSecondary;
  vars['--color-text-tertiary'] = theme.colors.textTertiary;
  vars['--color-text-inverse'] = theme.colors.textInverse;
  vars['--color-text-disabled'] = theme.colors.textDisabled;
  
  vars['--color-border'] = theme.colors.border;
  vars['--color-border-muted'] = theme.colors.borderMuted;
  vars['--color-border-strong'] = theme.colors.borderStrong;
  vars['--color-border-focus'] = theme.colors.borderFocus;
  
  vars['--color-success'] = theme.colors.success[500];
  vars['--color-warning'] = theme.colors.warning[500];
  vars['--color-danger'] = theme.colors.danger[500];
  vars['--color-info'] = theme.colors.info[500];
  
  for (let i = 1; i <= 8; i++) {
    vars[`--color-chart-${i}`] = theme.colors[`chart${i}` as keyof typeof theme.colors] as string;
  }
  
  vars['--scene-sky'] = theme.colors.sceneSky;
  vars['--scene-ground'] = theme.colors.sceneGround;
  vars['--scene-grid'] = theme.colors.sceneGrid;
  vars['--scene-ambient'] = theme.colors.sceneAmbient;
  vars['--scene-fog'] = theme.colors.sceneFog;
  vars['--scene-robot'] = theme.colors.sceneRobot;
  vars['--scene-path'] = theme.colors.scenePath;
  vars['--scene-detection'] = theme.colors.sceneDetection;
  
  vars['--shadow-sm'] = theme.shadows.sm;
  vars['--shadow-md'] = theme.shadows.md;
  vars['--shadow-lg'] = theme.shadows.lg;
  vars['--shadow-xl'] = theme.shadows.xl;
  vars['--shadow-glow'] = theme.shadows.glow;
  
  vars['--font-sans'] = theme.typography.fontFamily.sans;
  vars['--font-mono'] = theme.typography.fontFamily.mono;
  
  vars['--radius-sm'] = theme.radius.sm;
  vars['--radius-md'] = theme.radius.md;
  vars['--radius-lg'] = theme.radius.lg;
  
  vars['--duration-fast'] = theme.animation.duration.fast;
  vars['--duration-normal'] = theme.animation.duration.normal;
  vars['--duration-slow'] = theme.animation.duration.slow;
  
  return vars;
}
