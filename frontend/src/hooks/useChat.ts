import { useState, useCallback } from 'react';
import type { Message } from '../types';
import { usePipeline } from './usePipeline';
import { chat } from '../services/api';

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'msg-system-1',
      role: 'assistant',
      content: 'Olá! Sou o IMOBILAY, seu consultor de investimentos imobiliários. O que você procura hoje? (ex: Apartamento 2 quartos no Brooklin até 1M)',
      timestamp: new Date()
    }
  ]);
  const [isTyping, setIsTyping] = useState(false);
  const [sessionId] = useState(`sess-${Date.now()}`);
  
  const pipeline = usePipeline();
  // ⚡ Bolt Optimization: Destructure startPipeline so we don't depend on the entire
  // changing pipeline object in the useCallback, preventing sendMessage recreation.
  const { startPipeline } = pipeline;

  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim()) return;

    // Adiciona mensagem do usuário
    const userMsg: Message = {
      id: `msg-u-${Date.now()}`,
      role: 'user',
      content,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMsg]);
    setIsTyping(true);

    try {
      // Inicia o pipeline de análise visual
      const pipelinePromise = startPipeline();

      // Chama a API real do backend
      const response = await chat({
        message: content,
        session_id: sessionId
      });

      // Aguarda o pipeline terminar (se quisermos sincronizar a exibição)
      await pipelinePromise;

      // Adiciona a resposta real do assistente
      const assistantMsg: Message = {
        id: `msg-a-${Date.now()}`,
        role: 'assistant',
        content: response.response_text,
        timestamp: new Date(),
        contextData: response.context_data
      };

      setMessages(prev => [...prev, assistantMsg]);
    } catch (error) {
      console.error('Erro ao enviar mensagem:', error);
      
      const errorMsg: Message = {
        id: `msg-err-${Date.now()}`,
        role: 'assistant',
        content: 'Desculpe, tive um problema ao processar sua solicitação. Verifique se o backend está rodando.',
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsTyping(false);
    }
  }, [startPipeline, sessionId]);

  return {
    messages,
    isTyping,
    sendMessage,
    pipeline
  };
}
