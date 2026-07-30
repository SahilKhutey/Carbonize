export type ThemeMode = 'dark' | 'light' | 'auto';
export type ThemeName = 'default-dark' | 'default-light' | 'high-contrast' | 'mono' | 'custom' | string;

export interface ColorScale {
  50: string;
  100: string;
  200: string;
  300: string;
  400: string;
  500: string;
  600: string;
  700: string;
  800: string;
  900: string;
  950?: string;
}

export interface ThemeColors {
  primary: ColorScale;
  secondary: ColorScale;
  accent: ColorScale;
  
  success: ColorScale;
  warning: ColorScale;
  danger: ColorScale;
  info: ColorScale;
  
  background: string;
  surface: string;
  surfaceElevated: string;
  surfaceHover: string;
  surfaceActive: string;
  
  textPrimary: string;
  textSecondary: string;
  textTertiary: string;
  textInverse: string;
  textDisabled: string;
  
  border: string;
  borderMuted: string;
  borderStrong: string;
  borderFocus: string;
  
  chart1: string;
  chart2: string;
  chart3: string;
  chart4: string;
  chart5: string;
  chart6: string;
  chart7: string;
  chart8: string;
  
  sceneSky: string;
  sceneGround: string;
  sceneGrid: string;
  sceneAmbient: string;
  sceneFog: string;
  sceneRobot: string;
  scenePath: string;
  sceneDetection: string;
  
  overlay: string;
  overlayStrong: string;
  shadow: string;
  shadowStrong: string;
}

export interface ThemeSpacing {
  xs: string;
  sm: string;
  md: string;
  lg: string;
  xl: string;
  '2xl': string;
  '3xl': string;
}

export interface ThemeRadius {
  none: string;
  sm: string;
  md: string;
  lg: string;
  xl: string;
  '2xl': string;
  full: string;
}

export interface ThemeTypography {
  fontFamily: {
    sans: string;
    mono: string;
    display: string;
  };
  fontSize: {
    xs: string;
    sm: string;
    base: string;
    lg: string;
    xl: string;
    '2xl': string;
    '3xl': string;
    '4xl': string;
  };
  fontWeight: {
    normal: string;
    medium: string;
    semibold: string;
    bold: string;
  };
  lineHeight: {
    tight: string;
    normal: string;
    relaxed: string;
  };
}

export interface ThemeShadows {
  none: string;
  sm: string;
  md: string;
  lg: string;
  xl: string;
  '2xl': string;
  inner: string;
  glow: string;
}

export interface ThemeAnimation {
  duration: {
    fast: string;
    normal: string;
    slow: string;
  };
  easing: {
    linear: string;
    easeIn: string;
    easeOut: string;
    easeInOut: string;
  };
}

export interface Theme {
  id: ThemeName;
  name: string;
  description: string;
  mode: 'dark' | 'light';
  colors: ThemeColors;
  spacing: ThemeSpacing;
  radius: ThemeRadius;
  typography: ThemeTypography;
  shadows: ThemeShadows;
  animation: ThemeAnimation;
  custom?: boolean;
  createdAt?: string;
}

export interface ThemePreferences {
  theme: ThemeName;
  mode: ThemeMode;
  fontScale: number;
  motionReduced: boolean;
  highContrast: boolean;
}
