import { useReveal } from '../../hooks/useReveal';

const steps = [
  {
    num: 1,
    icon: '🧠',
    title: 'AI Screen',
    description: '12,000+ candidates evaluated daily using quantum chemistry, molecular dynamics, and property prediction',
    time: '⏱ 1 week',
  },
  {
    num: 2,
    icon: '🧪',
    title: 'Synthesize',
    description: 'Top 5 candidates made in lab after 3 weeks. Bench trials at 3 conditions: 40°C, 50°C, 70°C',
    time: '⏱ 3 weeks',
  },
  {
    num: 3,
    icon: '✓',
    title: 'Validate',
    description: '3 independent lab trials confirm predictions. 92.4% accuracy on known datasets',
    time: '⏱ 3 months',
  },
  {
    num: 4,
    icon: '🏭',
    title: 'Deploy',
    description: 'Pilot plant, 6 months. Continuous monitoring via our ops platform. Custom solvent for your conditions',
    time: '⏱ 6 months',
  },
];

export default function Solution() {
  const { ref, isVisible } = useReveal();

  return (
    <section id="solution" className="section" ref={ref}>
      <div className="max-w-6xl mx-auto px-6">
        <div className="text-center max-w-3xl mx-auto mb-20">
          <span className="section-eyebrow">How it works</span>
          <h2 className="section-title">From virtual screening to pilot plant in 6 months</h2>
          <p className="section-subtitle">
            AI-designed chemistry validated by physics, then proven in lab. 10× faster than traditional R&D.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {steps.map((step, idx) => (
            <div
              key={step.num}
              className={`step-card reveal ${isVisible ? 'visible' : ''}`}
              style={{ transitionDelay: `${idx * 0.1}s` }}
            >
              <div className="step-num">{step.num}</div>
              <div className="text-[2rem] mb-3">{step.icon}</div>
              <h3 className="text-xl font-bold mb-2">{step.title}</h3>
              <p className="text-sm text-slate-400">{step.description}</p>
              <div className="step-time">{step.time}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
