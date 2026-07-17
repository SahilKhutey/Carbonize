import { useState, useEffect, useRef } from 'react';

export interface SimulationRun {
  id: string;
  status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED';
  press_force_bar: number;
  enzyme_concentration_mg_l: number;
  chitosan_wt_pct: number;
  error_log?: string;
  pdf_report_url?: string;
  completed_at?: string;
  result?: {
    co2_capture_efficiency_pct: number;
    so2_capture_efficiency_pct: number;
    predicted_block_strength_mpa: number;
    block_grade: string;
    hourly_block_yield_kg: number;
    annual_block_count: number;
    estimated_opex_per_ton_co2: number;
    annual_ccts_revenue_inr: number;
    annual_block_revenue_inr: number;
    annual_opex_inr: number;
    annual_net_revenue_inr: number;
    capex_total_inr: number;
    simple_payback_months: number;
    npv_10yr_inr: number;
    irr_pct: number;
    mean_saturation_time_hours: number;
    p95_saturation_time_hours: number;
    cpcb_compliant: boolean;
  };
}

export function usePollingSimulation(runId: string | null) {
  const [simulation, setSimulation] = useState<SimulationRun | null>(null);
  const [loading, setLoading] = useState(false);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (!runId) {
      setSimulation(null);
      return;
    }

    const poll = async () => {
      try {
        setLoading(true);
        const res = await fetch(`/api/simulations/${runId}`);
        if (!res.ok) throw new Error('Simulation check failed.');
        const data = (await res.json()) as SimulationRun;
        setSimulation(data);

        if (data.status === 'COMPLETED' || data.status === 'FAILED') {
          setLoading(false);
          if (timerRef.current) clearInterval(timerRef.current);
        }
      } catch (err) {
        setLoading(false);
        if (timerRef.current) clearInterval(timerRef.current);
      }
    };

    poll();
    timerRef.current = setInterval(poll, 2000);

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [runId]);

  return { simulation, loading };
}
