import { useReveal } from '../../hooks/useReveal';

const validationData = [
  { value: '92.4%', label: 'Prediction accuracy', desc: 'Mean accuracy across 30+ published datasets' },
  { value: '0.97', label: 'R² (loading)', desc: 'Solvent capacity prediction' },
  { value: '0.95', label: 'R² (heat)', desc: 'Heat of absorption prediction' },
];

export default function Validation() {
  const { ref, isVisible } = useReveal();

  return (
    <section id="validation" className="section" ref={ref}>
      <div className="max-w-6xl mx-auto px-6">
        <div className="text-center max-w-3xl mx-auto mb-20">
          <span className="section-eyebrow">Validated</span>
          <h2 className="section-title">92.4% accuracy on 30+ published datasets</h2>
          <p className="section-subtitle">
            We don't trust our AI blindly. We benchmarked against MIT, Stanford, NREL, and 8 other published datasets.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {validationData.map((item, idx) => (
            <div
              key={idx}
              className={`validation-card reveal ${isVisible ? 'visible' : ''}`}
              style={{ transitionDelay: `${idx * 0.1}s` }}
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
