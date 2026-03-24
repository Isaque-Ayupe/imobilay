import React from 'react';

interface MetricCellProps {
  label: string;
  value: React.ReactNode;
  subValue?: React.ReactNode;
  highlight?: 'green' | 'coral' | 'neutral';
}

export function MetricCell({ label, value, subValue, highlight = 'neutral' }: MetricCellProps) {
  const highlightClasses = {
    green: 'text-green',
    coral: 'text-coral',
    neutral: 'text-text-primary'
  };

  return (
    <div className="flex flex-col gap-1 p-3 rounded-lg bg-surface border-[0.5px] border-border-mid">
      <span className="text-[10px] uppercase tracking-widest text-text-ghost font-medium">
        {label}
      </span>
      <div className={`font-display text-xl leading-none ${highlightClasses[highlight]}`}>
        {value}
      </div>
      {subValue && (
        <div className="text-xs text-text-muted mt-0.5">
          {subValue}
        </div>
      )}
    </div>
  );
}
