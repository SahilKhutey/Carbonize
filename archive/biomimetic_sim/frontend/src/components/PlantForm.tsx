import React, { useState } from 'react';

interface PlantFormProps {
  onSuccess: () => void;
}

export const PlantForm: React.FC<PlantFormProps> = ({ onSuccess }) => {
  const [formData, setFormData] = useState({
    name: '',
    location: '',
    industry_type: 'power_generation',
    boiler_type: 'pulverized_coal',
    exhaust_flow_rate: 10000,
    baseline_temperature: 150,
    co2_concentration: 14.0,
    so2_concentration: 1200,
    fly_ash_load: 45.0,
    nox_concentration: 500,
    water_cost_per_kl: 65,
    electricity_cost_per_kwh: 8.5,
    chitosan_cost_per_kg: 320,
    calcium_source_type: 'Ca(OH)2',
    calcium_cost_per_ton: 8500,
    local_brick_market_value: 12.0,
    ccts_credit_price: 1850
  });

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'number' ? parseFloat(value) : value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const res = await fetch('/api/plants', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Failed to submit plant profile.');
      }
      onSuccess();
    } catch (err: any) {
      setError(err.message || 'Something went wrong.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
      <div>
        <h2 className="text-lg font-bold text-white">Create Plant Profile</h2>
        <p className="text-xs text-slate-400 mt-1">Calibrate emissions parameters and local utility cost indicators.</p>
      </div>

      {error && (
        <div className="p-3 bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs rounded-lg">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
        {/* Basic Metadata */}
        <div className="flex flex-col gap-1.5">
          <label className="text-slate-400 font-medium">Plant Name</label>
          <input type="text" name="name" value={formData.name} onChange={handleChange} required className="bg-slate-950 border border-slate-800 rounded-lg p-2 text-white focus:outline-none focus:border-emerald-500" />
        </div>
        <div className="flex flex-col gap-1.5">
          <label className="text-slate-400 font-medium">Location</label>
          <input type="text" name="location" value={formData.location} onChange={handleChange} required className="bg-slate-950 border border-slate-800 rounded-lg p-2 text-white focus:outline-none focus:border-emerald-500" />
        </div>

        {/* Industry Types */}
        <div className="flex flex-col gap-1.5">
          <label className="text-slate-400 font-medium">Industry Segment</label>
          <select name="industry_type" value={formData.industry_type} onChange={handleChange} className="bg-slate-950 border border-slate-800 rounded-lg p-2 text-white focus:outline-none focus:border-emerald-500">
            <option value="power_generation">Power Generation</option>
            <option value="cement_manufacturing">Cement Manufacturing</option>
            <option value="steel_industry">Steel Industry</option>
          </select>
        </div>
        <div className="flex flex-col gap-1.5">
          <label className="text-slate-400 font-medium">Boiler/Kiln Tech</label>
          <select name="boiler_type" value={formData.boiler_type} onChange={handleChange} className="bg-slate-950 border border-slate-800 rounded-lg p-2 text-white focus:outline-none focus:border-emerald-500">
            <option value="pulverized_coal">Pulverized Coal Boiler</option>
            <option value="cfb">Circulating Fluidized Bed (CFB)</option>
            <option value="rotary_kiln">Rotary Kiln</option>
          </select>
        </div>

        {/* Flue Gas Parameters */}
        <div className="flex flex-col gap-1.5">
          <label className="text-slate-400 font-medium">Gas Flow Rate (Nm³/hr)</label>
          <input type="number" name="exhaust_flow_rate" value={formData.exhaust_flow_rate} onChange={handleChange} required className="bg-slate-950 border border-slate-800 rounded-lg p-2 text-white focus:outline-none focus:border-emerald-500" />
        </div>
        <div className="flex flex-col gap-1.5">
          <label className="text-slate-400 font-medium">CO₂ Concentration (vol %)</label>
          <input type="number" step="0.1" name="co2_concentration" value={formData.co2_concentration} onChange={handleChange} required className="bg-slate-950 border border-slate-800 rounded-lg p-2 text-white focus:outline-none focus:border-emerald-500" />
        </div>
        <div className="flex flex-col gap-1.5">
          <label className="text-slate-400 font-medium">SO₂ Concentration (mg/Nm³)</label>
          <input type="number" name="so2_concentration" value={formData.so2_concentration} onChange={handleChange} required className="bg-slate-950 border border-slate-800 rounded-lg p-2 text-white focus:outline-none focus:border-emerald-500" />
        </div>
        <div className="flex flex-col gap-1.5">
          <label className="text-slate-400 font-medium">Fly Ash Load (g/Nm³)</label>
          <input type="number" step="0.1" name="fly_ash_load" value={formData.fly_ash_load} onChange={handleChange} required className="bg-slate-950 border border-slate-800 rounded-lg p-2 text-white focus:outline-none focus:border-emerald-500" />
        </div>
      </div>

      <button type="submit" disabled={submitting} className="w-full bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold py-2.5 rounded-lg transition-all text-xs disabled:opacity-50">
        {submitting ? 'Creating Profile...' : 'Save Plant Profile'}
      </button>
    </form>
  );
};
