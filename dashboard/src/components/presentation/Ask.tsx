import { useReveal } from '../../hooks/useReveal';

const useOfFunds = [
  { pct: '40%', label: 'Engineering' },
  { pct: '30%', label: 'Sales' },
  { pct: '20%', label: 'Customer Success' },
  { pct: '10%', label: 'G&A' },
];

const askMetrics = [
  { label: 'Runway', value: '18 months' },
  { label: 'Target ARR (18mo)', value: '$1M' },
  { label: 'Customers (18mo)', value: '5 pilots' },
  { label: 'Valid Solvents', value: '10' },
];

export default function Ask() {
  const { ref, isVisible } = useReveal();

  return (
    <section id="ask" className="section" ref={ref}>
      <div className="max-w-6xl mx-auto px-6">
        <div className="ask-card reveal">
          <div className="text-center max-w-3xl mx-auto mb-12">
            <span className="section-eyebrow">The Ask</span>
            <h2 className="section-title">$10M Series A</h2>
            <p className="section-subtitle">
              18-month runway to take SOLV-0237 to 50 plants and validated solvent library to 10.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-[1fr_2fr] gap-12 items-center">
            <div className="ask-headline gradient-text">$10M</div>
            <div className="flex flex-col gap-4">
              {askMetrics.map((m, idx) => (
                <div key={idx} className="ask-metric">
                  <span className="ask-metric-label">{m.label}</span>
                  <span className="ask-metric-value">{m.value}</span>
                </div>
              ))}
            </div>
          </div>

          <h3 className="text-xl font-bold mt-16 mb-6">Use of funds</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {useOfFunds.map((f, idx) => (
              <div key={idx} className="fund-item">
                <div className="fund-pct">{f.pct}</div>
                <div className="fund-label">{f.label}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
