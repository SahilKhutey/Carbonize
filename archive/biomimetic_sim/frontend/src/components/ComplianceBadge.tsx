import React from 'react';

interface ComplianceBadgeProps {
  cpcbCompliant: boolean;
  value: number;
}

export const ComplianceBadge: React.FC<ComplianceBadgeProps> = ({ cpcbCompliant, value }) => {
  return (
    <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full border text-xs font-semibold w-fit ${
      cpcbCompliant
        ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400'
        : 'bg-rose-500/10 border-rose-500/20 text-rose-400'
    }`}>
      <span className={`w-2 h-2 rounded-full ${
        cpcbCompliant ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500'
      }`} />
      <span>
        CPCB Compliance: {cpcbCompliant ? 'PASS' : 'FAIL'} ({value.toFixed(1)} mg/Nm³)
      </span>
    </div>
  );
};
