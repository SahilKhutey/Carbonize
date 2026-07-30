import { useReveal } from '../../hooks/useReveal';

const marketData = [
  { size: '$50B', tier: 'TAM (Total Addressable Market)', desc: 'Global industrial point-source carbon capture equipment & solvent market', primary: false },
  { size: '$200B', tier: 'SAM (Serviceable Addressable)', desc: 'Projected global CCUS market by 2030 driven by IRA 45Q & EU ETS carbon prices', primary: false },
  { size: '$10M', tier: 'SOM (Serviceable Obtainable)', desc: 'Series A 18-month target: 50 industrial plants across cement, steel & power', primary: true },
];

export default function Market() {
  const { ref, isVisible } = useReveal();

  return (
    <section id="market" className="section section-bg" ref={ref}>
      <div className="max-w-6xl mx-auto px-6">
        <div className="text-center max-w-3xl mx-auto mb-20">
          <span className="section-eyebrow">Market Opportunity</span>
          <h2 className="section-title">$50B TAM Growing to $200B by 2030</h2>
          <p className="section-subtitle">
            Point-source decarbonization for 600+ cement plants, steel mills, and power stations requiring high-performance absorbents.
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
