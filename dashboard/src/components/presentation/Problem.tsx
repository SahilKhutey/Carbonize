import { useReveal } from '../../hooks/useReveal';

export default function Problem() {
  const { ref, isVisible } = useReveal();

  return (
    <section id="problem" className="section section-bg" ref={ref}>
      <div className="max-w-6xl mx-auto px-6">
        <div className="text-center max-w-3xl mx-auto mb-20">
          <span className="section-eyebrow">The Industrial Bottleneck</span>
          <h2 className="section-title">Legacy Amine Chemistry Costs $50–$80/Ton</h2>
          <p className="section-subtitle">
            Regenerating 30 wt% MEA requires 3.60 GJ/t CO₂ in thermal reboiler duty. Solvent makeup accounts for 35% of plant OPEX, with 1.50 kg/t chemical degradation.
            Carbonize replaces 5 years of physical trial-and-error with 6-month AI-designed solvent discovery.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-16 items-center">
          <div className="flex flex-col gap-5">
            <div className={`problem-card reveal ${isVisible ? 'visible' : ''}`}>
              <div className="problem-metric">3.60 GJ/t</div>
              <div className="text-sm text-slate-300 font-medium mb-2">Baseline MEA Regeneration Duty</div>
              <p className="text-sm text-slate-400">High heat of absorption (85.0 kJ/mol) requires massive low-pressure steam consumption, driving up plant energy costs.</p>
            </div>
            <div className={`problem-card reveal ${isVisible ? 'visible' : ''}`} style={{ transitionDelay: '0.1s' }}>
              <div className="problem-metric">5+ Years</div>
              <div className="text-sm text-slate-300 font-medium mb-2">Traditional Solvent Discovery Time</div>
              <p className="text-sm text-slate-400">Traditional empirical solvent R&D costs over $50M per molecule with a 98% failure rate in pilot scaling.</p>
            </div>
            <div className={`problem-card reveal ${isVisible ? 'visible' : ''}`} style={{ transitionDelay: '0.2s' }}>
              <div className="problem-metric">1.50 kg/t</div>
              <div className="text-sm text-slate-300 font-medium mb-2">MEA Thermal & Oxidative Degradation</div>
              <p className="text-sm text-slate-400">Standard monoethanolamine breaks down into corrosive carbamate species, requiring continuous chemical makeup and reclaimers.</p>
            </div>
          </div>

          <div className="solution-card">
            <h3 className="text-[1.75rem] font-extrabold mb-4">Our AI Chemistry Engine</h3>
            <p className="text-emerald-300 text-lg mb-6">
              We compress 5 years of absorbent R&D into 6 months using multi-scale physics & deep neural screening.
            </p>
            <ul className="flex flex-col gap-3 list-none">
              <li className="flex items-center gap-3 text-slate-300">
                <span className="check-icon">✓</span>
                12,000+ virtual amine candidates screened daily
              </li>
              <li className="flex items-center gap-3 text-slate-300">
                <span className="check-icon">✓</span>
                5 high-scoring candidates synthesized in 3 weeks
              </li>
              <li className="flex items-center gap-3 text-slate-300">
                <span className="check-icon">✓</span>
                3 independent lab bench & pilot trials validated
              </li>
              <li className="flex items-center gap-3 text-slate-300">
                <span className="check-icon">✓</span>
                1 hero molecule (SOLV-0237) achieving 2.45 GJ/t CO₂
              </li>
              <li className="flex items-center gap-3 text-slate-300">
                <span className="check-icon">✓</span>
                92.4% prediction accuracy against published NIST/MIT datasets
              </li>
            </ul>
          </div>
        </div>
      </div>
    </section>
  );
}
