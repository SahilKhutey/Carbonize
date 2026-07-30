import { useReveal } from '../../hooks/useReveal';

export default function Problem() {
  const { ref, isVisible } = useReveal();

  return (
    <section id="problem" className="section section-bg" ref={ref}>
      <div className="max-w-6xl mx-auto px-6">
        <div className="text-center max-w-3xl mx-auto mb-20">
          <span className="section-eyebrow">The Problem</span>
          <h2 className="section-title">The chemistry is the bottleneck.</h2>
          <p className="section-subtitle">
            $50/ton to capture CO₂. Solvent is 30–50% of OPEX. Today's amines (MEA) degrade 15% per year.
            600+ plants need this. We need 10× cost reduction for gigaton-scale deployment.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-16 items-center">
          <div className="flex flex-col gap-5">
            <div className={`problem-card reveal ${isVisible ? 'visible' : ''}`}>
              <div className="problem-metric">$50/ton</div>
              <div className="text-sm text-slate-300 font-medium mb-2">Current capture cost</div>
              <p className="text-sm text-slate-400">Carbon capture is 2–3× more expensive than alternatives. Solvent alone is 30–50% of OPEX.</p>
            </div>
            <div className={`problem-card reveal ${isVisible ? 'visible' : ''}`} style={{ transitionDelay: '0.1s' }}>
              <div className="problem-metric">5 years</div>
              <div className="text-sm text-slate-300 font-medium mb-2">Discovery time</div>
              <p className="text-sm text-slate-400">Traditional solvent R&D takes 5+ years, $50M+. One candidate survives. Industry stuck with incremental improvements.</p>
            </div>
            <div className={`problem-card reveal ${isVisible ? 'visible' : ''}`} style={{ transitionDelay: '0.2s' }}>
              <div className="problem-metric">15%/yr</div>
              <div className="text-sm text-slate-300 font-medium mb-2">MEA degradation</div>
              <p className="text-sm text-slate-400">Today's amines break down rapidly. Plants lose 5–15% capture efficiency annually. Solvent makeup is a huge cost.</p>
            </div>
          </div>

          <div className="solution-card">
            <h3 className="text-[1.75rem] font-extrabold mb-4">Our Solution</h3>
            <p className="text-emerald-300 text-lg mb-6">
              We use AI to design new absorption solvents in 6 months instead of 5 years.
            </p>
            <ul className="flex flex-col gap-3 list-none">
              <li className="flex items-center gap-3 text-slate-300">
                <span className="check-icon">✓</span>
                12,000+ virtual solvents screened per day
              </li>
              <li className="flex items-center gap-3 text-slate-300">
                <span className="check-icon">✓</span>
                5 synthesized in lab after 3 weeks
              </li>
              <li className="flex items-center gap-3 text-slate-300">
                <span className="check-icon">✓</span>
                3 validated in bench trials
              </li>
              <li className="flex items-center gap-3 text-slate-300">
                <span className="check-icon">✓</span>
                1 runway-ready breakthrough molecule
              </li>
              <li className="flex items-center gap-3 text-slate-300">
                <span className="check-icon">✓</span>
                92% prediction accuracy validated
              </li>
            </ul>
          </div>
        </div>
      </div>
    </section>
  );
}
