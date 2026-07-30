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
          <span className="text-[13px] text-emerald-300 font-medium">92.4% accuracy across 30+ published lab datasets</span>
        </div>

        <h1 className={`text-[clamp(2.5rem,7vw,5rem)] font-black leading-[1.05] tracking-[-0.04em] mb-6 reveal ${isVisible ? 'visible' : ''}`}>
          Industrial Carbon Capture<br />
          <span className="gradient-text">At $21.6M Annual OPEX Savings</span>
        </h1>

        <p className="text-[clamp(1.1rem,2.2vw,1.4rem)] text-slate-300 max-w-3xl mx-auto mb-10">
          AI-designed absorbents that outperform 30 wt% MEA by <strong className="text-emerald-400">31.9% in energy</strong> (2.45 vs 3.60 GJ/t CO₂),
          <strong className="text-cyan-400"> 18.0% in capacity</strong> (0.69 mol/mol), and <strong className="text-emerald-400">88% lower degradation</strong> (0.18 kg/t CO₂).
          Validated in 20-tray Wang-Henke simulation & 3 independent lab trials.
        </p>

        <div className="flex flex-wrap gap-4 justify-center mb-16">
          <a href="#roi" className="btn btn-primary btn-lg">
            Calculate Plant ROI (1.9 Mo Payback)
          </a>
          <a href="#solv-237" className="btn btn-secondary btn-lg">
            Explore SOLV-0237 Benchmarks
          </a>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-4xl mx-auto">
          <div className="stat-card">
            <div className="stat-value">31.9%</div>
            <div className="text-[13px] text-slate-300 font-medium">Energy Duty Reduction</div>
            <div className="text-[11px] text-slate-500 mt-1">2.45 vs 3.60 GJ/t CO₂</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">0.69</div>
            <div className="text-[13px] text-slate-300 font-medium">CO₂ Loading Capacity</div>
            <div className="text-[11px] text-slate-500 mt-1">mol CO₂ / mol amine</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">0.18 kg</div>
            <div className="text-[13px] text-slate-300 font-medium">Solvent Loss per Ton</div>
            <div className="text-[11px] text-slate-500 mt-1">vs 1.50 kg/t MEA baseline</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">$141.1M</div>
            <div className="text-[13px] text-slate-300 font-medium">10-Year Net Present Value</div>
            <div className="text-[11px] text-slate-500 mt-1">1,000,000 t/yr Mega Plant</div>
          </div>
        </div>
      </div>
    </header>
  );
}
