import React, { useRef, useEffect } from 'react';
import { SendHorizontal } from 'lucide-react';
import { motion } from 'framer-motion';

interface ChatInputProps {
  onSendMessage: (msg: string) => void;
  disabled?: boolean;
}

export function ChatInput({ onSendMessage, disabled }: ChatInputProps) {
  const [text, setText] = React.useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSend = () => {
    if (text.trim() && !disabled) {
      onSendMessage(text);
      setText('');
      if (textareaRef.current) {
        textareaRef.current.style.height = '56px';
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  useEffect(() => {
    const el = textareaRef.current;
    if (el) {
      el.style.height = '56px'; // height base
      const scrollHeight = el.scrollHeight;
      if (text) {
        el.style.height = Math.min(scrollHeight, 160) + 'px';
      }
    }
  }, [text]);

  return (
    <div className="w-full max-w-4xl mx-auto p-4 md:p-6">
      <div className="relative flex items-end bg-surface border-[0.5px] border-border-mid rounded-2xl shadow-sm focus-within:border-[var(--gold)] focus-within:ring-1 focus-within:ring-[var(--gold)]/20 transition-all duration-300">
        <textarea
          ref={textareaRef}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Descreva o imóvel ou investimento desejado..."
          className="w-full max-h-[160px] min-h-[56px] py-4 pl-4 pr-14 bg-transparent resize-none outline-none text-text-primary placeholder:text-text-ghost text-[15px] leading-relaxed"
          disabled={disabled}
        />
        <div className="absolute right-3 bottom-3">
          <motion.button
            whileTap={{ scale: 0.93 }}
            onClick={handleSend}
            disabled={!text.trim() || disabled}
            className={`w-9 h-9 rounded-xl flex items-center justify-center transition-colors
              ${text.trim() && !disabled 
                ? 'bg-[var(--gold)] text-white shadow-md' 
                : 'bg-surface-alt text-text-ghost cursor-not-allowed'}`}
          >
            <SendHorizontal className="w-4 h-4 ml-0.5" />
          </motion.button>
        </div>
      </div>
      <div className="mt-3 text-center">
        <p className="text-[10px] text-text-ghost tracking-wide">
          O IMOBILAY PODE COMETER ERROS. CONSIDERE VERIFICAR DADOS IMPORTANTES.
        </p>
      </div>
    </div>
  );
}
