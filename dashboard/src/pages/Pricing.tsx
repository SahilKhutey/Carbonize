import React from 'react';
import { Link } from 'react-router-dom';
import { Check, Star } from 'lucide-react';

export function PricingPage() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans py-24 px-6">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-5xl font-extrabold text-white mb-4">Performance-Aligned Pricing</h1>
          <p className="text-xl text-slate-400 max-w-2xl mx-auto">
            Pay for verified OPEX reduction. Zero capital risk for plant operators.
          </p>
        </div>
        
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          <PricingTier
            name="Pilot Trial"
            price="$250k"
            period="6-month engagement"
            description="Single plant bench & pilot skid validation"
            features={[
              'Custom solvent optimization for flue gas',
              '3-month bench-scale validation',
              '3-month on-site skid deployment',
              '15% OPEX reduction guarantee',
              'Full technical & financial report',
              'Custom IP licensing options',
            ]}
          />
          <PricingTier
            name="Platform License"
            price="$50k–$500k"
            period="per year / plant"
            description="Continuous operations & predictive digital twin"
            features={[
              'Real-time streaming telemetry dashboard',
              'ML anomaly detection & drift alerts',
              'Chaos engineering resilience testing',
              'Sensor degradation prediction',
              'Quarterly solvent formulation tuning',
              '24/7 technical support SLA',
            ]}
            highlight
          />
          <PricingTier
            name="Performance Share"
            price="$0.50–$2.00"
            period="per ton CO₂ captured"
            description="Shared savings model"
            features={[
              'Pay purely out of verified OPEX savings',
              'Independent 3rd-party measurement & audit',
              'Annual true-up reconciliation',
              'Indexed to actual energy reduction',
              'Zero upfront capital commitment',
            ]}
          />
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8 text-center max-w-3xl mx-auto">
          <h2 className="text-2xl font-bold text-white mb-2">Want to test SOLV-0237 on your plant data?</h2>
          <p className="text-slate-400 mb-6">Explore the interactive ROI calculator with custom capacity and steam cost parameters.</p>
          <Link to="/demo/roi" className="px-6 py-3 bg-emerald-500 hover:bg-emerald-600 text-white rounded-xl font-bold transition inline-block">
            Launch ROI Calculator →
          </Link>
        </div>
      </div>
    </div>
  );
}

function PricingTier({ name, price, period, description, features, highlight }: any) {
  return (
    <div className={`bg-slate-900 border-2 rounded-2xl p-8 flex flex-col justify-between ${
      highlight ? 'border-emerald-500 ring-4 ring-emerald-500/20' : 'border-slate-800'
    }`}>
      <div>
        {highlight && (
          <div className="inline-flex items-center gap-1 px-3 py-1 bg-emerald-500 text-white text-xs font-bold rounded-full mb-4">
            <Star className="w-3 h-3" />
            Recommended Tier
          </div>
        )}
        <h3 className="text-2xl font-bold text-white mb-2">{name}</h3>
        <div className="text-4xl font-extrabold text-emerald-400 mb-1">{price}</div>
        <div className="text-sm text-slate-400 mb-4">{period}</div>
        <p className="text-slate-300 text-sm mb-6">{description}</p>
        <ul className="space-y-3 mb-8">
          {features.map((f: string, i: number) => (
            <li key={i} className="flex items-start gap-2 text-sm text-slate-300">
              <Check className="w-5 h-5 flex-shrink-0 text-emerald-400" />
              {f}
            </li>
          ))}
        </ul>
      </div>
      <Link to="/demo/contact" className={`block text-center px-6 py-3 rounded-xl font-bold transition ${
        highlight
          ? 'bg-gradient-to-r from-emerald-500 to-cyan-500 hover:from-emerald-600 hover:to-cyan-600 text-white'
          : 'bg-slate-800 hover:bg-slate-700 text-slate-100 border border-slate-700'
      }`}>
        Schedule Scoping Call
      </Link>
    </div>
  );
}
