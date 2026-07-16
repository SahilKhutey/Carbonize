/**
 * packages/web/src/features/executive/types/executive.ts
 *
 * Executive / Report view types.
 */

export type { UserRole, AuthUser } from "../../operator/types/operator";

// ---------------------------------------------------------------------------
// Portfolio
// ---------------------------------------------------------------------------

export interface PortfolioKPI {
  id: string;
  label: string;
  value: string;
  unit: string;
  /** Signed percentage vs prior period, e.g. +12 or -3 */
  changePct: number;
  periodLabel: string; // "Month-to-Date", "Year-to-Date", etc.
  trend: "up" | "down" | "flat";
}

export interface PortfolioSummary {
  kpis: PortfolioKPI[];
  lastUpdated: string;
}

// ---------------------------------------------------------------------------
// Plant table
// ---------------------------------------------------------------------------

export type PlantStatus = "ok" | "warning" | "fault" | "offline";

export interface PlantRow {
  id: string;
  name: string;
  location: string;
  status: PlantStatus;
  co2CapturePct: number;
  npvCrorePerYear: number;
  cctsTonnes: number;
  lastMaintenanceDaysAgo: number;
}

// ---------------------------------------------------------------------------
// Trend charts
// ---------------------------------------------------------------------------

export interface TrendPoint {
  date: string;    // ISO date "YYYY-MM-DD"
  value: number;
}

export interface TrendSeries {
  plantId: string;
  plantName: string;
  metric: string;
  unit: string;
  data: TrendPoint[];
}

// ---------------------------------------------------------------------------
// Insights
// ---------------------------------------------------------------------------

export interface AutoInsight {
  id: string;
  plantId: string;
  plantName: string;
  title: string;
  summary: string;
  severity: "info" | "warning" | "opportunity";
  detectedAt: string;
  drillDownUrl?: string;
}

// ---------------------------------------------------------------------------
// Filters
// ---------------------------------------------------------------------------

export interface GlobalFilters {
  period: "7d" | "30d" | "90d" | "1y" | "custom";
  region?: string;
  plantIds?: string[];
}
