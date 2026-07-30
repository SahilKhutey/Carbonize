import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { CheckCircle, Send, Calendar } from 'lucide-react';
import demoApi from '@/api/demo';

const INITIAL = {
  contact_name: '',
  company_name: '',
  email: '',
  plant_capacity: '1000000',
  pilot_start_date: '2026-10-01',
  use_case: 'co2_capture',
  notes: '',
};

export function ContactView() {
  const [form, setForm] = useState(INITIAL);
  const [submitted, setSubmitted] = useState(false);

  const { mutate, isPending } = useMutation({
    mutationFn: (params: typeof INITIAL) => demoApi.submitProposal({
      contact_name: params.contact_name,
      company_name: params.company_name,
      email: params.email,
      plant_capacity_mt_per_year: Number(params.plant_capacity),
      pilot_start_date: params.pilot_start_date,
      use_case: params.use_case,
      notes: params.notes,
    }),
    onSuccess: () => setSubmitted(true),
  });

  const handle = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }));
  };

  if (submitted) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-100 font-sans flex items-center justify-center px-6">
        <div className="max-w-lg w-full text-center space-y-6">
          <div className="w-20 h-20 bg-emerald-500/20 border-2 border-emerald-500/50 rounded-full flex items-center justify-center mx-auto">
            <CheckCircle className="w-10 h-10 text-emerald-400" />
          </div>
          <h1 className="text-3xl font-bold text-white">Pilot Proposal Submitted!</h1>
          <p className="text-slate-400">
            Thanks, <strong className="text-white">{form.contact_name}</strong>. We'll send a tailored 3-month pilot proposal
            for <strong className="text-white">{form.company_name}</strong> to <strong className="text-white">{form.email}</strong> within 24 hours.
          </p>
          <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6 text-left space-y-2 text-sm">
            <div className="text-slate-400">What happens next:</div>
            <div className="flex items-center gap-2 text-slate-200"><CheckCircle className="w-4 h-4 text-emerald-400" /> Proposal PDF within 24h</div>
            <div className="flex items-center gap-2 text-slate-200"><CheckCircle className="w-4 h-4 text-emerald-400" /> 30-min technical call with chemistry team</div>
            <div className="flex items-center gap-2 text-slate-200"><CheckCircle className="w-4 h-4 text-emerald-400" /> Digital twin demo on your plant parameters</div>
            <div className="flex items-center gap-2 text-slate-200"><CheckCircle className="w-4 h-4 text-emerald-400" /> Pilot LOI signing — 3 months</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans py-20 px-6">
      <div className="max-w-2xl mx-auto space-y-8">
        <div className="text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-emerald-500/10 border border-emerald-500/30 rounded-full mb-4">
            <Calendar className="w-4 h-4 text-emerald-400" />
            <span className="text-xs text-emerald-300 font-semibold">Schedule a Pilot</span>
          </div>
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-2">Let's Get Your Plant Started</h1>
          <p className="text-slate-400">Fill out this form and we'll send you a customised 3-month pilot proposal within 24 hours.</p>
        </div>

        <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-8 space-y-5">
          <div className="grid md:grid-cols-2 gap-4">
            <Field label="Your Name" name="contact_name" value={form.contact_name} onChange={handle} placeholder="Jane Smith" />
            <Field label="Company / Plant" name="company_name" value={form.company_name} onChange={handle} placeholder="ACME Power Co." />
          </div>
          <Field label="Email Address" name="email" value={form.email} onChange={handle} placeholder="jane@acmeplant.com" type="email" />
          <div className="grid md:grid-cols-2 gap-4">
            <Field label="Plant Capacity (t CO₂/yr)" name="plant_capacity" value={form.plant_capacity} onChange={handle} placeholder="1000000" type="number" />
            <Field label="Preferred Pilot Start" name="pilot_start_date" value={form.pilot_start_date} onChange={handle} type="date" />
          </div>
          <div className="space-y-1">
            <label className="block text-xs font-semibold text-slate-300">Primary Use Case</label>
            <select
              name="use_case"
              value={form.use_case}
              onChange={handle}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 text-white text-sm focus:border-emerald-500 outline-none transition"
            >
              <option value="co2_capture">Post-combustion CO₂ capture (power)</option>
              <option value="dac">Direct Air Capture (DAC)</option>
              <option value="natural_gas">Natural gas sweetening</option>
              <option value="industrial">Industrial process decarbonisation</option>
            </select>
          </div>
          <div className="space-y-1">
            <label className="block text-xs font-semibold text-slate-300">Additional Notes (optional)</label>
            <textarea
              name="notes"
              value={form.notes}
              onChange={handle}
              rows={3}
              placeholder="Current solvent, key pain points, timeline constraints…"
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 text-white text-sm focus:border-emerald-500 outline-none transition resize-none"
            />
          </div>

          <button
            onClick={() => mutate(form)}
            disabled={isPending || !form.contact_name || !form.email || !form.company_name}
            className="w-full py-4 bg-gradient-to-r from-emerald-500 to-cyan-500 hover:from-emerald-600 hover:to-cyan-600 disabled:opacity-50 text-white rounded-xl font-bold text-base flex items-center justify-center gap-2 transition"
          >
            {isPending ? 'Generating Proposal…' : <><Send className="w-5 h-5" /> Request Pilot Proposal</>}
          </button>
        </div>

        <p className="text-center text-xs text-slate-500">
          We respect your privacy. Your information is used only to generate your pilot proposal.
        </p>
      </div>
    </div>
  );
}

function Field({ label, name, value, onChange, placeholder, type = 'text' }: any) {
  return (
    <div className="space-y-1">
      <label className="block text-xs font-semibold text-slate-300">{label}</label>
      <input
        type={type}
        name={name}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 text-white text-sm focus:border-emerald-500 outline-none transition"
      />
    </div>
  );
}
