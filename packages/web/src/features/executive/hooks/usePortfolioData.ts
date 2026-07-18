/**
 * packages/web/src/features/executive/hooks/usePortfolioData.ts
 *
 * Polls the portfolio analytics REST APIs on a 60-second interval.
 * Caches results in local state to avoid UI flicker.
 */

import { useState, useEffect, useCallback, useRef } from "react";
import type {
  PortfolioSummary, PlantRow, AutoInsight, GlobalFilters, PlantStatus,
} from "../types/executive";

const POLL_INTERVAL_MS = 60_000;

// ---------------------------------------------------------------------------
// Mock data (replace with real API calls when backend ready)
// ---------------------------------------------------------------------------

const MOCK_KPIS: PortfolioSummary = {
  kpis: [
    {
      id: "co2_captured",
      label: "CO₂ Captured",
      value: "2,847",
      unit: "tonnes",
      changePct: 12,
      periodLabel: "Month-to-Date",
      trend: "up",
    },
    {
      id: "ccts_credits",
      label: "CCTS Credits",
      value: "₹52,00,000",
      unit: "",
      changePct: 8,
      periodLabel: "Year-to-Date",
      trend: "up",
    },
    {
      id: "cost_savings",
      label: "Cost Savings",
      value: "₹18.2 Cr",
      unit: "",
      changePct: 24,
      periodLabel: "Year-to-Date",
      trend: "up",
    },
    {
      id: "active_plants",
      label: "Active Plants",
      value: "23",
      unit: "",
      changePct: 0,
      periodLabel: "",
      trend: "flat",
    },
    {
      id: "avg_capture",
      label: "Avg Capture",
      value: "85.4",
      unit: "%",
      changePct: 2.1,
      periodLabel: "vs last quarter",
      trend: "up",
    },
    {
      id: "intensity",
      label: "CO₂ Intensity",
      value: "0.42",
      unit: "tCO₂/MWh",
      changePct: -6.7,
      periodLabel: "YoY improvement",
      trend: "down",
    },
  ],
  lastUpdated: new Date().toISOString(),
};

const MOCK_PLANTS: PlantRow[] = [
  {
    id: "p1", name: "Plant A — Pune",      location: "Pune, MH",      status: "ok",      co2CapturePct: 87.2, npvCrorePerYear: 4.2, cctsTonnes: 450, lastMaintenanceDaysAgo: 12 },
  { id: "p2", name: "Plant B — Nashik",    location: "Nashik, MH",    status: "warning", co2CapturePct: 78.3, npvCrorePerYear: 3.8, cctsTonnes: 420, lastMaintenanceDaysAgo: 45 },
  { id: "p3", name: "Plant C — Nagpur",    location: "Nagpur, MH",    status: "ok",      co2CapturePct: 91.5, npvCrorePerYear: 5.1, cctsTonnes: 520, lastMaintenanceDaysAgo: 8  },
  { id: "p4", name: "Plant D — Raipur",    location: "Raipur, CG",    status: "fault",   co2CapturePct: 52.1, npvCrorePerYear: 1.2, cctsTonnes: 210, lastMaintenanceDaysAgo: 72 },
  { id: "p5", name: "Plant E — Bhopal",    location: "Bhopal, MP",    status: "ok",      co2CapturePct: 89.0, npvCrorePerYear: 4.7, cctsTonnes: 490, lastMaintenanceDaysAgo: 3  },
];

const MOCK_INSIGHTS: AutoInsight[] = [
  {
    id: "ins-1",
    plantId: "p2",
    plantName: "Plant B — Nashik",
    title: "CO₂ capture fell 8% in week 14",
    summary: "Possible causes: enzyme concentration drift, sensor recalibration due, or reagent pump degradation.",
    severity: "warning",
    detectedAt: "2026-04-08T09:00:00Z",
    drillDownUrl: "/executive/plants/p2",
  },
  {
    id: "ins-2",
    plantId: "p3",
    plantName: "Plant C — Nagpur",
    title: "NPV on track to exceed projection by 14%",
    summary: "Based on current capture rate and CCTS spot price trending above FY26 budget assumption.",
    severity: "opportunity",
    detectedAt: "2026-07-11T08:00:00Z",
    drillDownUrl: "/executive/plants/p3",
  },
];

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------

interface PortfolioData {
  summary: PortfolioSummary | null;
  plants: PlantRow[];
  insights: AutoInsight[];
  loading: boolean;
  error: string | null;
  refresh: () => void;
}

export function usePortfolioData(_filters?: GlobalFilters): PortfolioData {
  const [summary, setSummary] = useState<PortfolioSummary | null>(null);
  const [plants, setPlants] = useState<PlantRow[]>([]);
  const [insights, setInsights] = useState<AutoInsight[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params = new URLSearchParams();
      if (_filters?.period) params.append("period", _filters.period);
      if (_filters?.region) params.append("region", _filters.region);
      if (_filters?.plantIds) params.append("plantIds", _filters.plantIds.join(","));
      
      const queryString = params.toString() ? `?${params.toString()}` : "";
      const res = await fetch(`/api/analytics/portfolio${queryString}`);
      if (!res.ok) {
        throw new Error(`Failed to load portfolio analytics (Status ${res.status})`);
      }
      const data = await res.json();
      
      setSummary(data.summary);
      setPlants(data.plants || []);
      setInsights(data.insights || []);
    } catch (e: unknown) {
      setError((e as Error).message ?? "Failed to load portfolio data");
    } finally {
      setLoading(false);
    }
  }, [_filters]);

  useEffect(() => {
    fetchData();
    timerRef.current = setInterval(fetchData, POLL_INTERVAL_MS);
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [fetchData]);

  return { summary, plants, insights, loading, error, refresh: fetchData };
}
