import { useEffect, useRef } from 'react';
import type { Message } from '../../types';
import { MessageBubble } from './MessageBubble';
import type { PipelineStep } from '../../hooks/usePipeline';

interface MessageListProps {
  messages: Message[];
  isTyping: boolean;
  pipelineSteps: PipelineStep[];
  isPipelineActive: boolean;
}

export function MessageList({ messages, isTyping, pipelineSteps, isPipelineActive }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);
  
  // Scroll anchoring: sempre que mensagens mudam ou pipeline muda de status
  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isTyping, isPipelineActive]);

  // ⚡ Bolt Optimization: Memoize the temporary message object to prevent O(N) re-renders
  // in MessageBubble when isTyping or pipelineSteps change frequently.
  const tempMessage = useMemo(() => ({
    id: 'temp-processing',
    role: 'assistant' as const,
    content: '',
    timestamp: new Date()
  }), []);

  // ⚡ Bolt Optimization: Memoize empty array to prevent inline array instantiation
  // defeating React.memo when isPipelineActive is false.
  const EMPTY_STEPS = useMemo(() => [], []);

  return (
    <div className="flex-1 overflow-y-auto px-4 md:px-8 xl:px-24 pt-6 pb-12 w-full max-w-5xl mx-auto">
      {messages.map((msg) => {
        // Se for a última mensagem e o usuário acabou de enviar (então o assistente está respondendo)
        // Isso não acontece porque a msg do assistente só entra depois, mas podemos aplicar pipelineSteps
        // a uma mensagem temporária do sistema, ou diretamente renderizar um pending state fora do array.
        
        return (
          <MessageBubble key={msg.id} message={msg} />
        );
      })}

      {/* Estado de Processamento Ativo */}
      {(isTyping || isPipelineActive) && (
        <MessageBubble
          isProcessing={true}
          pipelineSteps={isPipelineActive ? pipelineSteps : EMPTY_STEPS}
          message={tempMessage}
        />
      )}
      
      <div ref={bottomRef} className="h-4" />
    </div>
  );
}
