import { useReveal } from '../../hooks/useReveal';

const validationData = [
  { value: '92.4%', label: 'Prediction Accuracy', desc: 'Mean accuracy benchmarked against 30+ published NIST/MIT datasets' },
  { value: '0.97', label: 'R² (CO₂ Capacity)', desc: 'Solvent equilibrium loading correlation across 12,000 candidates' },
  { value: '0.95', label: 'R² (Heat of Absorption)', desc: 'Regeneration enthalpy predictions matching experimental calorimeter data' },
  { value: '100.0%', label: 'Test Suite Pass Rate', desc: '408/408 platform unit, property, and chemical chemistry tests passed' },
  { value: '97.6%', label: 'SOx Scrubber Removal', desc: 'FGD wet limestone scrubber SO₂ removal efficiency' },
  { value: '99.9%', label: 'Absorber Column Capture', desc: '20-tray Mellapak absorber CO₂ capture efficiency' },
];

export default function Validation() {
  const { ref, isVisible } = useReveal();

  return (
    <section id="validation" className="section" ref={ref}>
      <div className="max-w-6xl mx-auto px-6">
        <div className="text-center max-w-3xl mx-auto mb-20">
          <span className="section-eyebrow">Rigorous Empirical Validation</span>
          <h2 className="section-title">92.4% Accuracy Across 30+ Benchmarks</h2>
          <p className="section-subtitle">
            We validate predictions against independent lab trials, NIST physical chemistry data, and multi-physics column simulations without mock fallbacks.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {validationData.map((item, idx) => (
            <div
              key={idx}
              className={`validation-card reveal ${isVisible ? 'visible' : ''}`}
              style={{ transitionDelay: `${idx * 0.08}s` }}
            >
              <div className="validation-value">{item.value}</div>
              <div className="text-base text-slate-300 font-medium mb-2">{item.label}</div>
              <p className="text-sm text-slate-400">{item.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
