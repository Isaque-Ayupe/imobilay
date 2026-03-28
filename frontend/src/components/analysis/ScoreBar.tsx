import { memo } from 'react';
import { motion } from 'framer-motion';

interface ScoreBarProps {
  label: string;
  score: number; // 0 to 10
  delay?: number;
}

// ⚡ Bolt Optimization:
// React.memo prevents unnecessary re-renders when parent component
// receives unrelated state updates like pipeline status.
export const ScoreBar = memo(function ScoreBar({ label, score, delay = 0 }: ScoreBarProps) {
  // Garantir que score esteja entre 0 e 10
  const normalizedScore = Math.max(0, Math.min(10, score));
  const percentage = (normalizedScore / 10) * 100;

  return (
    <div className="flex items-center gap-3 w-full my-1.5">
      <span className="w-28 text-xs text-text-muted shrink-0 font-medium">{label}</span>
      <div className="flex-1 h-1.5 bg-border rounded-full overflow-hidden flex relative">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 0.7, delay, ease: [0.16, 1, 0.3, 1] }}
          className="h-full bg-[var(--gold)] rounded-full absolute left-0 top-0"
        />
      </div>
      <span className="w-8 flex-shrink-0 text-right text-xs font-semibold text-text-primary">
        {normalizedScore.toFixed(1)}
      </span>
    </div>
  );
});
