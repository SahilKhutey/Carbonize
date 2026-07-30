import { useReveal } from '../../hooks/useReveal';

const comparisonData = [
  { property: 'CO₂ Loading Capacity (40°C, 1 atm)', us: '0.69 mol/mol', them: '0.50 mol/mol', improvement: '+38.0%', good: true },
  { property: 'Heat of Absorption (ΔH_abs)', us: '62.4 kJ/mol', them: '85.0 kJ/mol', improvement: '−26.6%', good: true },
  { property: 'Absorption Rate Constant (k₂ at 40°C)', us: '95.2 s⁻¹', them: '50.0 s⁻¹', improvement: '+90.4%', good: true },
  { property: 'Degradation & Makeup Rate', us: '0.18 kg/t CO₂', them: '1.50 kg/t CO₂', improvement: '−88.0%', good: true },
  { property: 'Reboiler Heat Duty Requirement', us: '2.45 GJ/t CO₂', them: '3.60 GJ/t CO₂', improvement: '−31.9%', good: true },
  { property: 'Toxicity (Oral Rat LD₅₀)', us: '2,840 mg/kg', them: '1,500 mg/kg', improvement: '+89.3%', good: true },
];

export default function Solv237() {
  const { ref, isVisible } = useReveal();

  return (
    <section id="solv-237" className="section solv-bg" ref={ref}>
      <div className="max-w-6xl mx-auto px-6">
        <div className="text-center max-w-3xl mx-auto mb-20">
          <span className="section-eyebrow">Tested & Validated Breakthrough Molecule</span>
          <h2 className="section-title">SOLV-0237 Chemistry Profile</h2>
          <p className="section-subtitle">
            Sterically-hindered bicyclic amine discovered via AI screening of 12,000+ candidates. Synthesized in 3 weeks and benchmarked against 30 wt% MEA across 6 physical chemistry parameters.
          </p>
        </div>

        <div className={`solv-hero-card reveal ${isVisible ? 'visible' : ''}`}>
          <div className="solv-badge">★ Tested Hero Molecule</div>
          <h2 className="text-[3rem] font-black mb-2 tracking-[-0.02em]">SOLV-0237</h2>
          <div className="text-emerald-300 text-xl mb-4">Sterically-Hindered Bicyclic Amine (C₈H₁₅NO)</div>
          <p className="text-slate-400 text-base mb-8">
            Density: 0.942 g/cm³ · Boiling Point: 418.2 K · Viscosity: 3.42 mPa·s · Vapor Pressure: 12.4 Pa at 40°C
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
            <div className="solv-stat">
              <div className="solv-stat-value">31.9%</div>
              <div className="text-[13px] text-slate-300 font-medium">Reboiler Heat Duty Reduction</div>
              <div className="text-[11px] text-slate-500 mt-1">2.45 GJ/t vs 3.60 GJ/t MEA</div>
            </div>
            <div className="solv-stat">
              <div className="solv-stat-value">0.69</div>
              <div className="text-[13px] text-slate-300 font-medium">Equilibrium CO₂ Loading</div>
              <div className="text-[11px] text-slate-500 mt-1">mol CO₂ / mol amine</div>
            </div>
            <div className="solv-stat">
              <div className="solv-stat-value">88.0%</div>
              <div className="text-[13px] text-slate-300 font-medium">Lower Degradation Loss</div>
              <div className="text-[11px] text-slate-500 mt-1">0.18 kg/t vs 1.50 kg/t MEA</div>
            </div>
          </div>
        </div>

        <div className="comparison-wrapper overflow-x-auto">
          <table className="comparison-table">
            <thead>
              <tr>
                <th>Physical / Chemical Property</th>
                <th className="us">SOLV-0237 (Tested)</th>
                <th className="competitor">30 wt% MEA Baseline</th>
                <th>Measured Improvement</th>
              </tr>
            </thead>
            <tbody>
              {comparisonData.map((row, idx) => (
                <tr key={idx}>
                  <td className="text-slate-300">{row.property}</td>
                  <td className="us">{row.us}</td>
                  <td className="competitor">{row.them}</td>
                  <td className={row.good ? 'improvement-good' : 'improvement'}>
                    {row.improvement}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}
