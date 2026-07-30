import { useReveal } from '../../hooks/useReveal';

const milestones = [
  {
    quarter: 'Q1 2025',
    title: 'Pilot Kickoff',
    desc: '3 paid pilots signed. SOLV-0237 deployed at first cement plant.',
    right: '✓ 3 LOIs',
    rightTitle: '$750k pilot revenue',
    rightDesc: '2 customers up and running by end of Q1.',
  },
  {
    quarter: 'Q2 2025',
    title: 'Platform Launch',
    desc: 'Production-grade platform. SOC 2 Type II audit. 99.9% uptime SLA.',
    right: '✓ SOC 2',
    rightTitle: 'SOC 2 Type II',
    rightDesc: 'Complete security audit. Enterprise-ready compliance.',
  },
  {
    quarter: 'Q3 2025',
    title: '5 Validated Solvents',
    desc: 'Expand pipeline from 1 to 5 validated solvents for different conditions.',
    right: '✓ 5×',
    rightTitle: 'Solvent portfolio',
    rightDesc: 'Each optimized for different conditions and industries.',
  },
  {
    quarter: 'Q4 2025',
    title: 'Series A Raise',
    desc: '$10M raise at $50M valuation. 5 pilots completed. $5M pipeline.',
    right: '$10M',
    rightTitle: 'Series A',
    rightDesc: 'Scale to 20 plants, 50 validated solvents, $XM ARR.',
  },
];

export default function Roadmap() {
  const { ref, isVisible } = useReveal();

  return (
    <section id="roadmap" className="section section-bg" ref={ref}>
      <div className="max-w-6xl mx-auto px-6">
        <div className="text-center max-w-3xl mx-auto mb-20">
          <span className="section-eyebrow">Roadmap</span>
          <h2 className="section-title">18-month plan to $1M ARR</h2>
          <p className="section-subtitle">
            From 3 pilots to $5M pipeline. From 1 solvent to 10 validated.
          </p>
        </div>

        <div className="timeline max-w-5xl mx-auto relative">
          <div className="absolute left-1/2 top-0 bottom-0 w-0.5 bg-gradient-to-b from-transparent via-emerald-500 to-transparent transform -translate-x-1/2" />

          {milestones.map((m, idx) => (
            <div
              key={idx}
              className={`grid grid-cols-1 md:grid-cols-[1fr_auto_1fr] gap-8 mb-12 items-center reveal ${isVisible ? 'visible' : ''}`}
              style={{ transitionDelay: `${idx * 0.1}s` }}
            >
              <div className="text-right">
                <div className="timeline-quarter">{m.quarter}</div>
                <div className="timeline-title">{m.title}</div>
                <p className="timeline-desc">{m.desc}</p>
              </div>
              <div className="timeline-center">{idx + 1}</div>
              <div className="text-left">
                <div className="timeline-quarter">{m.right}</div>
                <div className="timeline-title">{m.rightTitle}</div>
                <p className="timeline-desc">{m.rightDesc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
