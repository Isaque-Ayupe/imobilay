import { useState, useCallback } from 'react';
import type { Message } from '../types';
import { MOCK_CONTEXT_DATA } from '../data/mock';
import { usePipeline } from './usePipeline';

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
  
  const pipeline = usePipeline();

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

    // Inicia o pipeline de análise
    await pipeline.startPipeline();

    // Adiciona a resposta do assistente baseada no mock
    const assistantMsg: Message = {
      id: `msg-a-${Date.now()}`,
      role: 'assistant',
      content: 'Com base na sua busca, localizei 2 imóveis em Pinheiros. Ambos apresentam dados favoráveis, mas a primeira opção se destaca pelo desvio negativo de preço, gerando maior potencial de investimento. Abaixo está a análise estruturada:',
      timestamp: new Date(),
      contextData: MOCK_CONTEXT_DATA
    };

    setMessages(prev => [...prev, assistantMsg]);
    setIsTyping(false);
  }, [pipeline]);

  return {
    messages,
    isTyping,
    sendMessage,
    pipeline
  };
}
