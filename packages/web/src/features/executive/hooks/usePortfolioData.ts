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
