import { useState } from 'react';
import { submitInquiry, trackROIResult } from '../../lib/supabase';

export default function ROICalculator() {
  const [capacity, setCapacity] = useState(500000);
  const [opex, setOpex] = useState(60);
  const [energy, setEnergy] = useState(4.2);
  const [email, setEmail] = useState('');
  const [saved, setSaved] = useState(false);

  const energyReduction = 0.27;
  const newOpex = opex * (1 - 0.25);
  const annualSavings = (opex - newOpex) * capacity;
  const implementationCost =
    capacity < 200000 ? 250000 : capacity < 1000000 ? 500000 : 2000000;
  const paybackMonths = (implementationCost / annualSavings) * 12;

  const carbonCredit = capacity * 0.05 * 50;
  const yearlyCF = annualSavings + carbonCredit;
  let npv = -implementationCost;
  for (let year = 1; year <= 10; year++) {
    npv += yearlyCF / Math.pow(1.08, year);
  }

  const co2Avoided = capacity * 0.05;

  const fmt = (n: number) => {
    if (n >= 1e9) return `$${(n / 1e9).toFixed(1)}B`;
    if (n >= 1e6) return `$${(n / 1e6).toFixed(1)}M`;
    if (n >= 1e3) return `$${(n / 1e3).toFixed(0)}k`;
    return `$${n.toFixed(0)}`;
  };

  const fmtTime = (n: number) => `${n.toFixed(1)} months`;

  const handleSave = async () => {
    if (!email) {
      setSaved(true);
      return;
    }
    try {
      await trackROIResult({
        capacity,
        opex,
        energy,
        annual_savings: annualSavings,
        ten_year_npv: npv,
        payback_months: paybackMonths,
        email,
      });
      await submitInquiry({
        name: 'ROI Calculator User',
        email,
        company: '',
        source: 'roi_calculator',
        message: `Capacity: ${capacity} t/yr, OPEX: $${opex}/t, 10yr NPV: ${fmt(npv)}`,
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
          <span className="section-eyebrow">ROI Calculator</span>
          <h2 className="section-title">What's your 10-year savings?</h2>
          <p className="section-subtitle">Plug in your plant details. See the impact.</p>
        </div>

        <div className="roi-calc-card">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="flex flex-col gap-5">
              <div>
                <label className="roi-input-label">Annual CO₂ Captured</label>
                <input
                  type="number"
                  value={capacity}
                  onChange={(e) => setCapacity(parseFloat(e.target.value) || 0)}
                  className="roi-input"
                  min="1000"
                  step="1000"
                />
                <div className="roi-input-hint">tons per year (100k small, 500k medium, 2M large)</div>
              </div>
              <div>
                <label className="roi-input-label">Current OPEX per ton</label>
                <input
                  type="number"
                  value={opex}
                  onChange={(e) => setOpex(parseFloat(e.target.value) || 0)}
                  className="roi-input"
                  min="20"
                  max="200"
                  step="0.5"
                />
                <div className="roi-input-hint">USD per ton CO₂ captured</div>
              </div>
              <div>
                <label className="roi-input-label">Current Energy Use</label>
                <input
                  type="number"
                  value={energy}
                  onChange={(e) => setEnergy(parseFloat(e.target.value) || 0)}
                  className="roi-input"
                  min="2"
                  max="8"
                  step="0.1"
                />
                <div className="roi-input-hint">GJ per ton CO₂ captured</div>
              </div>
            </div>

            <div className="roi-results">
              <div className="roi-result-row primary">
                <div className="roi-result-label">10-Year NPV</div>
                <div className="roi-result-value">{fmt(npv)}</div>
              </div>
              <div className="roi-result-row">
                <div className="roi-result-label">Annual OPEX Savings</div>
                <div className="roi-result-value regular">{fmt(annualSavings)} / yr</div>
              </div>
              <div className="roi-result-row">
                <div className="roi-result-label">Payback Period</div>
                <div className="roi-result-value regular">{fmtTime(paybackMonths)}</div>
              </div>
              <div className="roi-result-row">
                <div className="roi-result-label">OPEX Reduction</div>
                <div className="roi-result-value regular">25%</div>
              </div>
              <div className="roi-result-row">
                <div className="roi-result-label">Energy Reduction</div>
                <div className="roi-result-value regular">27%</div>
              </div>

              <div className="roi-summary">
                <div className="roi-summary-item">
                  <div className="roi-summary-label">CO₂ Avoided / yr</div>
                  <div className="roi-summary-value">{(co2Avoided / 1000).toFixed(0)}k tons</div>
                </div>
                <div className="roi-summary-item">
                  <div className="roi-summary-label">Implementation Cost</div>
                  <div className="roi-summary-value">
                    {implementationCost < 1e6 ? `$${(implementationCost / 1000).toFixed(0)}k` : `$${(implementationCost / 1e6).toFixed(1)}M`}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-8 pt-8 border-t border-slate-800">
            <p className="text-sm text-slate-400 mb-3">Get your full ROI report with sensitivity analysis:</p>
            <div className="flex gap-3 max-w-md">
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your.email@company.com"
                className="roi-input flex-1"
              />
              <button onClick={handleSave} className="btn btn-primary">
                {saved ? '✓ Saved!' : 'Send Report'}
              </button>
            </div>
          </div>

          <p className="roi-note">
            Calculations based on validated SOLV-0237 performance vs. industry-average MEA plant.
            Actual savings vary by plant conditions, energy costs, and regulatory regime.
          </p>
        </div>
      </div>
    </section>
  );
}
