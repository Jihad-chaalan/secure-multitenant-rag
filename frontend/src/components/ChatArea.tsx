// src/components/ChatArea.tsx

import { useState, useRef, useEffect } from 'react';
import { useAppStore } from '../store/useAppStore';
import api from '../api/client';
import type { ChatResponse } from '../types';
import PerformanceChip from './PerformanceChip';
import SourceCard from './SourceCard';

export default function ChatArea() {
  const {
    department,
    role,
    messages,
    isLoading,
    sources,
    performance,
    addMessage,
    setIsLoading,
    setChatResult,
    addRequestLog,
  } = useAppStore();

  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    // 1. Add user message and clear input
    const userMsg = { role: 'user' as const, content: input };
    addMessage(userMsg);
    setInput('');
    setIsLoading(true);
    setChatResult([], null);

    try {
      // 2. Call the API
      const response = await api.post<ChatResponse>('/chat', {
        query: input,
        department,
        role,
        top_k: 5,
      });

      const data = response.data;

      // 3. Add assistant message
      addMessage({ role: 'assistant' as const, content: data.answer });

      // 4. Save sources and performance for the UI
      setChatResult(data.sources, data.performance);

      // 5. 🔥 Log the request for the Admin Dashboard
      addRequestLog({
        timestamp: new Date().toISOString(),
        query: input,
        department,
        role,
        latency_ms: data.performance.latency_ms,
        source_count: data.sources.length,
        status: 'success',
      });
    } catch (error) {
      // 6. Handle error
      addMessage({
        role: 'assistant' as const,
        content: 'Sorry, an error occurred. Please try again.',
      });

      // 7. 🔥 Log the failed request for the Admin Dashboard
      addRequestLog({
        timestamp: new Date().toISOString(),
        query: input,
        department,
        role,
        latency_ms: 0,
        source_count: 0,
        status: 'error',
      });

      console.error('Chat error:', error);
    } finally {
      // 8. Reset loading state
      setIsLoading(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col bg-white h-full">
      {/* Header with Performance Chip */}
      <div className="border-b border-gray-200 px-6 py-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-800">
          🗂️ {department} / {role}
        </h2>
        {performance && <PerformanceChip performance={performance} />}
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-400 mt-20">
            <p className="text-4xl mb-2">💬</p>
            <p>Ask me anything about your department's documents.</p>
            <p className="text-sm mt-1 text-gray-300">
              {department} / {role}
            </p>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-3xl rounded-lg px-4 py-3 ${
                msg.role === 'user'
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 text-gray-800'
              }`}
            >
              <p className="whitespace-pre-wrap">{msg.content}</p>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg px-4 py-3 text-gray-500">
              <span className="animate-pulse">▸</span> Thinking...
            </div>
          </div>
        )}

        {/* Sources Section (Collapsible Accordion) */}
        {!isLoading && sources.length > 0 && (
          <div className="mt-4">
            <details className="border border-gray-200 rounded-lg overflow-hidden bg-gray-50">
              <summary className="px-4 py-3 font-medium text-gray-700 cursor-pointer hover:bg-gray-100 transition flex items-center justify-between">
                <span>📚 {sources.length} Sources Retrieved</span>
                <span className="text-xs text-gray-400">Click to expand</span>
              </summary>
              <div className="p-4 space-y-3 border-t border-gray-200 bg-white">
                {sources.map((source, idx) => (
                  <SourceCard key={idx} source={source} index={idx} />
                ))}
              </div>
            </details>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-200 px-6 py-4 bg-white">
        <div className="flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask a question about your documents..."
            className="flex-1 border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition disabled:bg-gray-100"
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            disabled={isLoading || !input.trim()}
            className="bg-primary-600 text-white px-6 py-2.5 rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition font-medium"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}