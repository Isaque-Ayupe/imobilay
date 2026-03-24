import { Fragment } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import type { PipelineStep } from '../../hooks/usePipeline';

interface PipelineIndicatorProps {
  steps: PipelineStep[];
}

export function PipelineIndicator({ steps }: PipelineIndicatorProps) {
  return (
    <div className="flex flex-wrap items-center gap-2 my-4 p-4 rounded-xl border-[0.5px] border-border bg-surface-alt/50 w-fit">
      <AnimatePresence>
        {steps.map((step, index) => {
          const isActive = step.status === 'active';
          const isDone = step.status === 'done';

          return (
            <Fragment key={step.id}>
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.08, duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-[11px] uppercase tracking-wider font-medium font-sans border-[0.5px] transition-colors duration-500
                  ${isActive ? 'bg-[var(--gold)]/10 border-[var(--gold)]/30 text-[var(--gold)]' : ''}
                  ${isDone ? 'bg-green-light border-green/20 text-green' : ''}
                  ${!isActive && !isDone ? 'bg-transparent border-transparent text-text-ghost' : ''}
                `}
              >
                {isActive && (
                  <motion.div
                    animate={{ scale: [1, 1.2, 1] }}
                    transition={{ duration: 1.5, repeat: Infinity }}
                    className="w-1.5 h-1.5 rounded-full bg-[var(--gold)]"
                  />
                )}
                {isDone && (
                  <div className="w-1.5 h-1.5 rounded-full bg-green" />
                )}
                {!isActive && !isDone && (
                  <div className="w-1.5 h-1.5 rounded-full bg-text-ghost/30" />
                )}
                {step.label}
              </motion.div>
              
              {index < steps.length - 1 && (
                <motion.span
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: index * 0.08 + 0.1 }}
                  className="text-text-ghost/50 text-xs"
                >
                  ›
                </motion.span>
              )}
            </Fragment>
          );
        })}
      </AnimatePresence>
    </div>
  );
}
