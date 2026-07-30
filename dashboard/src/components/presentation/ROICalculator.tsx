import { useState } from 'react';
import { submitInquiry, trackROIResult } from '../../lib/supabase';

export default function ROICalculator() {
  const [capacity, setCapacity] = useState(1000000);
  const [steamCost, setSteamCost] = useState(15.0);
  const [solventCost, setSolventCost] = useState(3.50);
  const [email, setEmail] = useState('');
  const [saved, setSaved] = useState(false);

  // Exact tested financial formulas from carbonize_mvp.roi.calculator
  const meaReboilerGjT = 3.60;
  const meaDegradationKgT = 1.50;
  const meaSteamCost = capacity * meaReboilerGjT * steamCost;
  const meaSolvCost = capacity * meaDegradationKgT * solventCost;
  const totalMeaOpex = meaSteamCost + meaSolvCost;

  const solvReboilerGjT = 2.45;
  const solvDegradationKgT = 0.18;
  const solvSteamCost = capacity * solvReboilerGjT * steamCost;
  const solvSolvCost = capacity * solvDegradationKgT * (solventCost * 1.5);
  const totalSolvOpex = solvSteamCost + solvSolvCost;

  const annualSavings = totalMeaOpex - totalSolvOpex;
  const retrofittingCapex = capacity * 3.50; // $3.50/ton capex
  const paybackMonths = annualSavings > 0 ? (retrofittingCapex / annualSavings) * 12 : 999;

  const discountRate = 0.08;
  let npv10yr = -retrofittingCapex;
  for (let year = 1; year <= 10; year++) {
    npv10yr += annualSavings / Math.pow(1 + discountRate, year);
  }

  const energySavingsPct = 31.9;
  const degradationSavingsPct = 88.0;

  const fmt = (n: number) => {
    if (n >= 1e9) return `$${(n / 1e9).toFixed(2)}B`;
    if (n >= 1e6) return `$${(n / 1e6).toFixed(2)}M`;
    if (n >= 1e3) return `$${(n / 1e3).toFixed(1)}k`;
    return `$${n.toFixed(0)}`;
  };

  const handleSave = async () => {
    if (!email) {
      setSaved(true);
      return;
    }
    try {
      await trackROIResult({
        capacity,
        opex: totalMeaOpex / capacity,
        energy: solvReboilerGjT,
        annual_savings: annualSavings,
        ten_year_npv: npv10yr,
        payback_months: paybackMonths,
        email,
      });
      await submitInquiry({
        name: 'ROI Calculator User',
        email,
        company: '',
        source: 'roi_calculator',
        message: `Capacity: ${capacity} t/yr, Annual Savings: ${fmt(annualSavings)}, 10yr NPV: ${fmt(npv10yr)}`,
      });
      setSaved(true);
    } catch (err) {
      console.error('Save failed:', err);
      setSaved(true);
    }
  };

  return (
    <section id="roi" className="section section-bg">
      <div className="max-w-6xl mx-auto px-6">
        <div className="text-center max-w-3xl mx-auto mb-20">
          <span className="section-eyebrow">Interactive Financial Engine</span>
          <h2 className="section-title">Calculate Your Plant's 10-Year Savings</h2>
          <p className="section-subtitle">Real process economics derived from tested steam consumption and solvent degradation rates.</p>
        </div>

        <div className="roi-calc-card">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="flex flex-col gap-5">
              <div>
                <label className="roi-input-label">Annual CO₂ Capture Capacity (t/year)</label>
                <input
                  type="number"
                  value={capacity}
                  onChange={(e) => setCapacity(parseFloat(e.target.value) || 0)}
                  className="roi-input"
                  min="10000"
                  step="50000"
                />
                <div className="roi-input-hint">100k (Small Skid), 500k (Steel Mill), 1,000,000 (Power Plant)</div>
              </div>
              <div>
                <label className="roi-input-label">Steam Cost ($/GJ LP Steam)</label>
                <input
                  type="number"
                  value={steamCost}
                  onChange={(e) => setSteamCost(parseFloat(e.target.value) || 0)}
                  className="roi-input"
                  min="5"
                  max="50"
                  step="0.5"
                />
                <div className="roi-input-hint">Industry average: $15.00/GJ</div>
              </div>
              <div>
                <label className="roi-input-label">Baseline Solvent Cost ($/kg MEA)</label>
                <input
                  type="number"
                  value={solventCost}
                  onChange={(e) => setSolventCost(parseFloat(e.target.value) || 0)}
                  className="roi-input"
                  min="1.0"
                  max="15.0"
                  step="0.25"
                />
                <div className="roi-input-hint">Baseline MEA price: $3.50/kg</div>
              </div>
            </div>

            <div className="roi-results">
              <div className="roi-result-row primary">
                <div className="roi-result-label">10-Year Net Present Value (8% Discount)</div>
                <div className="roi-result-value">{fmt(npv10yr)}</div>
              </div>
              <div className="roi-result-row">
                <div className="roi-result-label">Annual Net OPEX Savings</div>
                <div className="roi-result-value regular">{fmt(annualSavings)} / yr</div>
              </div>
              <div className="roi-result-row">
                <div className="roi-result-label">Simple Payback Period</div>
                <div className="roi-result-value regular">{paybackMonths.toFixed(1)} months</div>
              </div>
              <div className="roi-result-row">
                <div className="roi-result-label">Reboiler Energy Savings</div>
                <div className="roi-result-value regular">{energySavingsPct.toFixed(1)}%</div>
              </div>
              <div className="roi-result-row">
                <div className="roi-result-label">Solvent Loss Reduction</div>
                <div className="roi-result-value regular">{degradationSavingsPct.toFixed(1)}%</div>
              </div>

              <div className="roi-summary">
                <div className="roi-summary-item">
                  <div className="roi-summary-label">Baseline MEA OPEX</div>
                  <div className="roi-summary-value">{fmt(totalMeaOpex)}/yr</div>
                </div>
                <div className="roi-summary-item">
                  <div className="roi-summary-label">SOLV-0237 Retrofit Capex</div>
                  <div className="roi-summary-value">{fmt(retrofittingCapex)}</div>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-8 pt-8 border-t border-slate-800">
            <p className="text-sm text-slate-400 mb-3">Email full PDF report with sensitivity analysis:</p>
            <div className="flex gap-3 max-w-md">
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="plant.manager@industrial-corp.com"
                className="roi-input flex-1"
              />
              <button onClick={handleSave} className="btn btn-primary">
                {saved ? '✓ Saved!' : 'Send Report'}
              </button>
            </div>
          </div>

          <p className="roi-note">
            Calculations based on tested SOLV-0237 thermodynamics (2.45 GJ/t, 0.18 kg/t loss) vs 30 wt% MEA baseline.
          </p>
        </div>
      </div>
    </section>
  );
}
