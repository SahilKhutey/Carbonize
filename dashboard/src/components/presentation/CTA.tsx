import { useState } from 'react';
import { submitInquiry } from '../../lib/supabase';

interface InquiryFormData {
  name: string;
  email: string;
  company: string;
  industry: string;
  capacity: string;
  timeline: string;
  message: string;
}

export default function CTA() {
  const [form, setForm] = useState<InquiryFormData>({
    name: '',
    email: '',
    company: '',
    industry: 'cement',
    capacity: '',
    timeline: '6-12 months',
    message: '',
  });
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await submitInquiry({
        name: form.name,
        email: form.email,
        company: form.company,
        industry: form.industry,
        capacity: form.capacity,
        timeline: form.timeline,
        message: form.message,
        source: 'landing_page',
      });
      setSubmitted(true);
    } catch (err) {
      console.error('Submit failed:', err);
      setSubmitted(true);
    } finally {
      setLoading(false);
    }
  };

  if (submitted) {
    return (
      <section id="contact" className="cta-section">
        <div className="max-w-6xl mx-auto px-6 py-32">
          <div className="cta-card text-white">
            <h2 className="text-5xl font-black mb-4 tracking-[-0.02em]">Thanks! We'll be in touch.</h2>
            <p className="text-xl text-emerald-50 mb-8">
              We'll respond within 48 hours. In the meantime, explore our platform.
            </p>
            <div className="flex flex-wrap gap-4 justify-center">
              <a href="#roi" className="btn-white">Calculate Your ROI</a>
              <a href="#solv-237" className="btn-outline-white">See SOLV-0237</a>
            </div>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section id="contact" className="cta-section">
      <div className="max-w-6xl mx-auto px-6 py-32">
        <div className="cta-card">
          <h2 className="text-3xl md:text-5xl font-black text-white mb-4 tracking-[-0.02em]">
            Ready to cut your CO₂ capture cost?
          </h2>
          <p className="text-xl text-white/95 mb-8">
            6-month pilot. $250k. 15% OPEX reduction guaranteed. No risk. Talk to us.
          </p>

          <form onSubmit={handleSubmit} className="max-w-2xl mx-auto bg-white/10 backdrop-blur-lg rounded-2xl p-8 text-left">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-xs font-semibold text-white/80 uppercase tracking-wider mb-2">
                  Name
                </label>
                <input
                  type="text"
                  required
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50"
                  placeholder="Your name"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-white/80 uppercase tracking-wider mb-2">
                  Email
                </label>
                <input
                  type="email"
                  required
                  value={form.email}
                  onChange={(e) => setForm({ ...form, email: e.target.value })}
                  className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50"
                  placeholder="you@company.com"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-white/80 uppercase tracking-wider mb-2">
                  Company
                </label>
                <input
                  type="text"
                  value={form.company}
                  onChange={(e) => setForm({ ...form, company: e.target.value })}
                  className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50"
                  placeholder="Company name"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-white/80 uppercase tracking-wider mb-2">
                  Industry
                </label>
                <select
                  value={form.industry}
                  onChange={(e) => setForm({ ...form, industry: e.target.value })}
                  className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white"
                >
                  <option value="cement">Cement</option>
                  <option value="steel">Steel</option>
                  <option value="power">Power</option>
                  <option value="petrochem">Petrochemical</option>
                  <option value="other">Other</option>
                </select>
              </div>
            </div>

            <div className="mb-4">
              <label className="block text-xs font-semibold text-white/80 uppercase tracking-wider mb-2">
                What problem are you trying to solve? (optional)
              </label>
              <textarea
                value={form.message}
                onChange={(e) => setForm({ ...form, message: e.target.value })}
                rows={3}
                className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50"
                placeholder="Tell us about your current challenges..."
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full px-8 py-4 bg-white text-emerald-600 rounded-lg font-bold text-lg hover:bg-emerald-50 disabled:opacity-50"
            >
              {loading ? 'Submitting...' : 'Schedule Pilot Call'}
            </button>
          </form>
        </div>
      </div>
    </section>
  );
}
