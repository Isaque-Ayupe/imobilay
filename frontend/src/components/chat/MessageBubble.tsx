import { memo, useMemo } from 'react';
import type { Message } from '../../types';
import type { PipelineStep } from '../../hooks/usePipeline';
import { motion } from 'framer-motion';

import { PropertyAnalysisCard } from '../analysis/PropertyAnalysisCard';
import { PipelineIndicator } from './PipelineIndicator';
import { TypingIndicator } from './TypingIndicator';


interface MessageBubbleProps {
  message: Message;
  pipelineSteps?: PipelineStep[]; // Only present if it's the active processing message
  isProcessing?: boolean;
}

// ⚡ Bolt Optimization:
// React.memo prevents O(N) unnecessary re-renders of all previous messages
// whenever the active pipeline status or typing indicator updates in the parent MessageList.
export const MessageBubble = memo(function MessageBubble({ message, pipelineSteps, isProcessing }: MessageBubbleProps) {

  // ⚡ Bolt Optimization:
  // Pre-compute lookup maps for O(1) access instead of O(N) array.find() on every render
  const analysisMaps = useMemo(() => {
    const valuationMap = new Map();
    const investmentMap = new Map();
    const opportunityMap = new Map();
    const rankingMap = new Map();

    if (message.contextData?.analysis) {
      message.contextData.analysis.valuation?.forEach(v => valuationMap.set(v.property_id, v));
      message.contextData.analysis.investment?.forEach(i => investmentMap.set(i.property_id, i));
      message.contextData.analysis.opportunities?.forEach(o => opportunityMap.set(o.property_id, o));
      message.contextData.analysis.ranking?.ranking?.forEach(r => rankingMap.set(r.property_id, r));
    }

    return { valuationMap, investmentMap, opportunityMap, rankingMap };
  }, [message.contextData]);

  const isUser = message.role === 'user';

  if (isUser) {
    return (
      <motion.div 
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
        className="flex w-full justify-end my-4"
      >
        <div className="max-w-[80%] md:max-w-[70%] bg-navy text-surface px-5 py-3.5" style={{ borderRadius: '14px 14px 3px 14px' }}>
          <p className="text-[14px] leading-relaxed whitespace-pre-wrap">{message.content}</p>
        </div>
      </motion.div>
    );
  }

  // Assistant Message
  return (
    <div className="flex flex-col w-full my-6 max-w-4xl">
      {/* Pipeline Indicator (apenas se tiver steps e for a mensagem atual) */}
      {pipelineSteps && pipelineSteps.length > 0 && (
        <PipelineIndicator steps={pipelineSteps} />
      )}

      {/* Typing Indicator */}
      {isProcessing && (!pipelineSteps || pipelineSteps.every(s => s.status === 'done')) && (
        <TypingIndicator />
      )}

      {/* Message Content */}
      {(!isProcessing || message.content) && (
        <motion.div 
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
          className="flex gap-4 items-start"
        >
          <div className="w-8 h-8 rounded shrink-0 bg-surface-alt border-[0.5px] border-border flex items-center justify-center text-[var(--gold)] font-display text-sm font-bold mt-1">
            IM
          </div>
          <div className="flex-1">
            <div className="bg-surface border-[0.5px] border-border px-5 py-4 text-text-primary text-[14.5px] leading-relaxed" style={{ borderRadius: '3px 14px 14px 14px' }}>
              <p className="whitespace-pre-wrap">{message.content}</p>
            </div>
            
            {/* Context Data (Análises Imobiliárias) */}
            {message.contextData?.properties && (
              <div className="mt-6 space-y-6">
                {message.contextData.properties.map(property => {
                  const valuation = analysisMaps.valuationMap.get(property.id);
                  const investment = analysisMaps.investmentMap.get(property.id);
                  const opportunity = analysisMaps.opportunityMap.get(property.id);
                  const ranking = analysisMaps.rankingMap.get(property.id);

                  return (
                    <PropertyAnalysisCard 
                      key={property.id}
                      property={property}
                      valuation={valuation}
                      investment={investment}
                      opportunity={opportunity}
                      ranking={ranking}
                    />
                  );
                })}
              </div>
            )}
          </div>
        </motion.div>
      )}
    </div>
  );
});
