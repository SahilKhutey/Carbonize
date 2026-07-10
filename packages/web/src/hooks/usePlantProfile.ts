import { useState, useEffect } from 'react';

export interface PlantProfile {
  id: string;
  name: string;
  location: string;
  boiler_type: string;
  exhaust_flow_rate: number;
  baseline_temperature: number;
  co2_concentration: number;
  so2_concentration: number;
  fly_ash_load: number;
  nox_concentration: number;
  logistics?: {
    water_cost_per_kl: number;
    electricity_cost_per_kwh: number;
    chitosan_cost_per_kg: number;
    calcium_source_type: string;
    calcium_cost_per_ton: number;
    local_brick_market_value: number;
    ccts_credit_price: number;
  };
}

export function usePlantProfile() {
  const [plants, setPlants] = useState<PlantProfile[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPlants = async () => {
    try {
      setLoading(true);
      const res = await fetch('/api/plants');
      if (!res.ok) throw new Error('Failed to fetch plant profiles.');
      const data = await res.json();
      setPlants(data);
    } catch (err: any) {
      setError(err.message || 'Something went wrong.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPlants();
  }, []);

  return { plants, loading, error, refresh: fetchPlants };
}
