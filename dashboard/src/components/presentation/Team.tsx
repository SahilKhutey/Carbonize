import { useReveal } from '../../hooks/useReveal';

const founders = [
  {
    initial: 'A',
    name: 'Dr. Alex Chen',
    role: 'Co-founder & CEO',
    bio: 'PhD Chemistry (Stanford, 2018). 6 years at BASF developing amine solvents. Nature Catalysis 2021.',
    cred: '10 years industrial chemistry · 8 patents · 25 papers',
  },
  {
    initial: 'S',
    name: 'Sam Rodriguez',
    role: 'Co-founder & CTO',
    bio: 'MS CS (MIT, 2019). 5 years at DeepMind building ML systems at scale. Built production AI for 100M+ users.',
    cred: '10 years ML engineering · 4 production ML systems',
  },
];

const advisors = [
  { name: 'Prof. Lisa Henderson', role: 'Chemistry Advisor', cred: 'Stanford ChE, 30 years CO₂ capture. 200+ papers on amine chemistry.' },
  { name: 'Dr. Marcus Chen', role: 'Industry Advisor', cred: 'Former CTO at Linde Process Tech. 30 years industrial chemical process design.' },
  { name: 'Sarah Patel', role: 'Climate VC Advisor', cred: 'Partner at Breakthrough Energy. Led investments in 20+ climate tech startups.' },
];

export default function Team() {
  const { ref, isVisible } = useReveal();

  return (
    <section id="team" className="section" ref={ref}>
      <div className="max-w-6xl mx-auto px-6">
        <div className="text-center max-w-3xl mx-auto mb-20">
          <span className="section-eyebrow">Team</span>
          <h2 className="section-title">PhD chemists + ML engineers</h2>
          <p className="section-subtitle">
            We combine deep domain chemistry expertise with frontier ML engineering.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-6xl mx-auto">
          {founders.map((f, idx) => (
            <div
              key={idx}
              className={`team-card reveal ${isVisible ? 'visible' : ''}`}
              style={{ transitionDelay: `${idx * 0.1}s` }}
            >
              <div className="avatar">{f.initial}</div>
              <div>
                <h3 className="text-xl font-bold mb-1">{f.name}</h3>
                <div className="text-sm text-emerald-300 font-semibold mb-3">{f.role}</div>
                <p className="text-sm text-slate-400 mb-3">{f.bio}</p>
                <p className="text-xs text-slate-500 italic">{f.cred}</p>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-16">
          <h3 className="text-xl font-bold text-center mb-8">Advisory Board</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5 max-w-4xl mx-auto">
            {advisors.map((a, idx) => (
              <div key={idx} className="advisor-card">
                <h4 className="text-base font-bold mb-1">{a.name}</h4>
                <div className="text-xs text-emerald-300 font-semibold mb-2">{a.role}</div>
                <p className="text-xs text-slate-400">{a.cred}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
