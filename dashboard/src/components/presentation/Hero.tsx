import { useReveal } from '../../hooks/useReveal';

export default function Hero() {
  const { ref, isVisible } = useReveal({ threshold: 0.1 });

  return (
    <header className="hero" ref={ref}>
      <div className="orb" style={{ width: 600, height: 600, background: 'radial-gradient(circle, #10b981, transparent)', top: -200, left: -200, position: 'absolute' }} />
      <div className="orb" style={{ width: 500, height: 500, background: 'radial-gradient(circle, #06b6d4, transparent)', bottom: -150, right: -150, position: 'absolute' }} />
      <div className="grid-bg" />

      <div className="max-w-6xl mx-auto px-6 text-center relative z-[2]">
        <div className={`inline-flex items-center gap-2 px-4 py-2 bg-emerald-500/10 border border-emerald-500/30 rounded-full mb-6 reveal ${isVisible ? 'visible' : ''}`}>
          <div className="pulse-dot" />
          <span className="text-[13px] text-emerald-300 font-medium">92% accuracy on 30+ published datasets</span>
        </div>

        <h1 className={`text-[clamp(2.5rem,7vw,5rem)] font-black leading-[1.05] tracking-[-0.04em] mb-6 reveal ${isVisible ? 'visible' : ''}`}>
          Industrial carbon capture<br />
          <span className="gradient-text">at half the cost</span>
        </h1>

        <p className="text-[clamp(1.1rem,2.2vw,1.4rem)] text-slate-300 max-w-3xl mx-auto mb-10">
          AI-designed absorbents that outperform MEA by 32% in energy,
          18% in capacity, and 3× in degradation resistance.
          Validated across 3 independent labs.
        </p>

        <div className="flex flex-wrap gap-4 justify-center mb-16">
          <a href="#roi" className="btn btn-primary btn-lg">
            Calculate Your ROI
          </a>
          <a href="#solv-237" className="btn btn-secondary btn-lg">
            See SOLV-0237
          </a>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-4xl mx-auto">
          <div className="stat-card">
            <div className="stat-value">32%</div>
            <div className="text-[13px] text-slate-300 font-medium">Energy reduction</div>
            <div className="text-[11px] text-slate-500 mt-1">vs. MEA</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">18%</div>
            <div className="text-[13px] text-slate-300 font-medium">Capacity gain</div>
            <div className="text-[11px] text-slate-500 mt-1">vs. MEA</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">3×</div>
            <div className="text-[13px] text-slate-300 font-medium">Degradation resistance</div>
            <div className="text-[11px] text-slate-500 mt-1">vs. MEA</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">$234M</div>
            <div className="text-[13px] text-slate-300 font-medium">10-yr NPV</div>
            <div className="text-[11px] text-slate-500 mt-1">1 Mt/yr plant</div>
          </div>
        </div>
      </div>
    </header>
  );
}
