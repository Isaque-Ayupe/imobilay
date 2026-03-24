import { Sidebar } from './components/layout/Sidebar';
import { TopBar } from './components/layout/TopBar';
import { ChatInput } from './components/chat/ChatInput';
import { MessageList } from './components/chat/MessageList';
import { useChat } from './hooks/useChat';

function App() {
  const { messages, isTyping, sendMessage, pipeline } = useChat();

  return (
    <div className="flex h-screen w-full bg-surface overflow-hidden antialiased">
      <Sidebar />
      <main className="flex-1 flex flex-col h-full bg-surface relative">
        <TopBar />
        
        {/* Chat Area - Scrollable */}
        <div className="flex-1 overflow-y-auto relative custom-scrollbar">
          <MessageList 
            messages={messages} 
            isTyping={isTyping} 
            pipelineSteps={pipeline.steps}
            isPipelineActive={pipeline.isActive}
          />
        </div>

        {/* Input Area - Fixed At Bottom */}
        <div className="w-full bg-surface border-t border-border-mid/50 pb-4 pt-2">
          <ChatInput onSendMessage={sendMessage} disabled={pipeline.isActive} />
        </div>
      </main>
    </div>
  );
}

export default App;
