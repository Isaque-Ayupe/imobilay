import { motion } from 'framer-motion';

export function TypingIndicator() {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex items-center gap-3 p-4 bg-surface-alt rounded-2xl rounded-tl-sm w-fit border-[0.5px] border-border"
    >
      <div className="w-6 h-6 rounded bg-[var(--gold)]/10 text-[var(--gold)] flex items-center justify-center text-[10px] font-display font-bold shrink-0">
        IM
      </div>
      <div className="flex gap-1.5 py-2 px-1">
        {[0, 1, 2].map((i) => (
          <motion.div
            key={i}
            animate={{ opacity: [0.3, 1, 0.3], scale: [0.9, 1.1, 0.9] }}
            transition={{ duration: 1.4, repeat: Infinity, delay: i * 0.2 }}
            className="w-1.5 h-1.5 rounded-full bg-[var(--gold)]"
          />
        ))}
      </div>
    </motion.div>
  );
}
