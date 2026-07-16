/**
 * packages/web/src/features/executive/index.tsx
 * Executive / Report feature barrel.
 */
export { ExecutiveDashboard } from "./pages/ExecutiveDashboard";
export { ExecNav }            from "./components/ExecNav";
export { PortfolioKPIs }      from "./components/PortfolioKPIs";
export { PlantTable }         from "./components/PlantTable";
export { AutoInsights }       from "./components/AutoInsights";
export { usePortfolioData }   from "./hooks/usePortfolioData";
export type {
  PortfolioKPI, PortfolioSummary, PlantRow, PlantStatus,
  TrendSeries, TrendPoint, AutoInsight, GlobalFilters,
} from "./types/executive";
