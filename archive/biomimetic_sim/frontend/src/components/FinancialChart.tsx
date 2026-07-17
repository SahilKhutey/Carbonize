import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts';

interface FinancialChartProps {
  annualOpex: number;
  annualBlockRevenue: number;
  annualCctsRevenue: number;
  capex: number;
}

export const FinancialChart: React.FC<FinancialChartProps> = ({
  annualOpex,
  annualBlockRevenue,
  annualCctsRevenue,
  capex
}) => {
  const data = [
    {
      name: 'Startup Costs (CAPEX)',
      Cost: capex / 1e5, // In Lakhs
      fill: '#f59e0b'
    },
    {
      name: 'Annual OPEX',
      Cost: annualOpex / 1e5,
      fill: '#ef4444'
    },
    {
      name: 'Block Sales Revenue',
      Cost: annualBlockRevenue / 1e5,
      fill: '#10b981'
    },
    {
      name: 'CCTS Credit Revenue',
      Cost: annualCctsRevenue / 1e5,
      fill: '#3b82f6'
    }
  ];

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-lg flex flex-col gap-4">
      <div>
        <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">
          Financial Sizing & Yield Analysis
        </h3>
        <p className="text-xs text-slate-500 mt-0.5">Expressed in Lakhs INR (₹ 1,00,000)</p>
      </div>

      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 20, right: 10, left: -20, bottom: 5 }}>
            <XAxis dataKey="name" stroke="#94a3b8" fontSize={10} tickLine={false} />
            <YAxis stroke="#94a3b8" fontSize={10} tickLine={false} />
            <Tooltip
              contentStyle={{ background: '#0f172a', border: '1px solid #334155', borderRadius: '8px' }}
              labelStyle={{ color: '#fff', fontSize: '11px', fontWeight: 'bold' }}
              itemStyle={{ fontSize: '11px' }}
              formatter={(value: any) => [`₹ ${Number(value).toFixed(2)} Lakhs`]}
            />
            <Bar dataKey="Cost" radius={[4, 4, 0, 0]}>
              {data.map((entry, index) => (
                <Bar key={`bar-${index}`} dataKey="Cost" fill={entry.fill} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
