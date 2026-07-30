import { useReveal } from '../../hooks/useReveal';

const comparisonData = [
  { property: 'CO₂ loading (40°C, 1 atm)', us: '0.69 mol/mol', them: '0.50 mol/mol', improvement: '+38%', good: true },
  { property: 'Heat of absorption', us: '62 kJ/mol', them: '85 kJ/mol', improvement: '−27%', good: true },
  { property: 'Absorption rate (40°C)', us: '95 1/s', them: '50 1/s', improvement: '+90%', good: true },
  { property: 'Degradation rate', us: '2.0%/yr', them: '15%/yr', improvement: '−87%', good: true },
  { property: 'Toxicity (LD50)', us: '2,800 mg/kg', them: '1,500 mg/kg', improvement: '+87%', good: false },
  { property: 'Cost', us: '$6.5/kg', them: '$2/kg', improvement: '+225%', good: false },
];

export default function Solv237() {
  const { ref, isVisible } = useReveal();

  return (
    <section id="solv-237" className="section solv-bg" ref={ref}>
      <div className="max-w-6xl mx-auto px-6">
        <div className="text-center max-w-3xl mx-auto mb-20">
          <span className="section-eyebrow">Meet SOLV-0237</span>
          <h2 className="section-title">Our breakthrough molecule</h2>
          <p className="section-subtitle">
            Top candidate from 12,000+ virtual solvents. Synthesized in 3 weeks. Validated in 3 lab trials.
          </p>
        </div>

        <div className={`solv-hero-card reveal ${isVisible ? 'visible' : ''}`}>
          <div className="solv-badge">★ Top Candidate</div>
          <h2 className="text-[3rem] font-black mb-2 tracking-[-0.02em]">SOLV-0237</h2>
          <div className="text-emerald-300 text-xl mb-4">A Sterically-Hindered Bicyclic Amine</div>
          <p className="text-slate-400 text-base mb-8">
            Discovered via AI screening of 12,000+ candidates · Synthesized in 3 weeks · Validated in 3 lab trials
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
            <div className="solv-stat">
              <div className="solv-stat-value">32%</div>
              <div className="text-[13px] text-slate-300 font-medium">Energy reduction</div>
              <div className="text-[11px] text-slate-500 mt-1">vs. MEA</div>
            </div>
            <div className="solv-stat">
              <div className="solv-stat-value">18%</div>
              <div className="text-[13px] text-slate-300 font-medium">Capacity gain</div>
              <div className="text-[11px] text-slate-500 mt-1">vs. MEA</div>
            </div>
            <div className="solv-stat">
              <div className="solv-stat-value">3×</div>
              <div className="text-[13px] text-slate-300 font-medium">Degradation resistance</div>
              <div className="text-[11px] text-slate-500 mt-1">vs. MEA</div>
            </div>
          </div>
        </div>

        <div className="comparison-wrapper overflow-x-auto">
          <table className="comparison-table">
            <thead>
              <tr>
                <th>Property</th>
                <th className="us">SOLV-0237</th>
                <th className="competitor">MEA</th>
                <th>Improvement</th>
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
