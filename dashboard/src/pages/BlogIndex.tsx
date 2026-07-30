import React from 'react';
import { Link } from 'react-router-dom';
import { Calendar, Clock, ArrowRight } from 'lucide-react';

const posts = [
  {
    slug: 'why-ai-chemistry-matters',
    title: 'Why AI-Designed Chemistry is the Key to Gigaton-Scale Carbon Capture',
    excerpt: 'The chemistry is the single largest bottleneck in CCUS. Traditional experimental R&D takes 5 years per candidate...',
    date: '2024-12-15',
    readTime: 8,
    author: 'Carbonize Research Team',
  },
  {
    slug: 'solv-237-case-study',
    title: 'SOLV-0237: How We Discovered a Breakthrough Amine in 6 Months',
    excerpt: 'A technical deep-dive into multi-objective Pareto optimization across loading, kinetics, heat of absorption, and thermal degradation...',
    date: '2024-12-08',
    readTime: 12,
    author: 'Carbonize Computational Chemistry',
  },
  {
    slug: 'roi-calculator-guide',
    title: 'Quantifying Industrial CO₂ Capture OPEX Reduction: Solvent Swap ROI',
    excerpt: 'A practical framework for plant engineers and CFOs evaluating energy savings, degradation reduction, and payback periods...',
    date: '2024-12-01',
    readTime: 6,
    author: 'Carbonize Engineering',
  },
];

export function BlogIndex() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans py-24 px-6">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-5xl font-extrabold text-white mb-4">Research & Technical Blog</h1>
          <p className="text-xl text-slate-400">
            Insights on AI solvent design, computational chemistry, and industrial CCUS deployment.
          </p>
        </div>
        
        <div className="space-y-8">
          {posts.map((post) => (
            <article key={post.slug} className="bg-slate-900 border border-slate-800 rounded-2xl p-8 hover:border-slate-700 transition">
              <div className="flex items-center gap-4 text-sm text-slate-400 mb-4">
                <div className="flex items-center gap-1">
                  <Calendar className="w-4 h-4 text-emerald-400" />
                  {post.date}
                </div>
                <div className="flex items-center gap-1">
                  <Clock className="w-4 h-4 text-cyan-400" />
                  {post.readTime} min read
                </div>
                <div className="text-slate-500">By {post.author}</div>
              </div>
              <h2 className="text-2xl font-bold text-white mb-3">
                {post.title}
              </h2>
              <p className="text-slate-400 mb-6">{post.excerpt}</p>
              <Link to="/demo" className="text-emerald-400 hover:text-emerald-300 font-bold flex items-center gap-2 text-sm">
                Explore Demo Console <ArrowRight className="w-4 h-4" />
              </Link>
            </article>
          ))}
        </div>
      </div>
    </div>
  );
}
