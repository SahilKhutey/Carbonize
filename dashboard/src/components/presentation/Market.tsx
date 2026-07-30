import { useReveal } from '../../hooks/useReveal';

const marketData = [
  { size: '$50B', tier: 'TAM', desc: 'Global CO₂ capture market today', primary: false },
  { size: '$200B', tier: 'SAM', desc: 'Solvent + monitoring by 2030', primary: false },
  { size: '$10M', tier: 'SOM', desc: '5-year reachable: 50 plants', primary: true },
];

export default function Market() {
  const { ref, isVisible } = useReveal();

  return (
    <section id="market" className="section section-bg" ref={ref}>
      <div className="max-w-6xl mx-auto px-6">
        <div className="text-center max-w-3xl mx-auto mb-20">
          <span className="section-eyebrow">Market</span>
          <h2 className="section-title">$50B TAM → $200B by 2030</h2>
          <p className="section-subtitle">
            Carbon capture is a 10× growth market. Climate targets demand gigaton-scale deployment.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {marketData.map((item, idx) => (
            <div
              key={idx}
              className={`market-card reveal ${isVisible ? 'visible' : ''} ${item.primary ? 'primary' : ''}`}
              style={{ transitionDelay: `${idx * 0.1}s` }}
            >
              <div className="market-size">{item.size}</div>
              <div className="text-sm text-slate-300 font-medium mb-2">{item.tier}</div>
              <p className="text-sm text-slate-400">{item.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
