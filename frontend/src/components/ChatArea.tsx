// src/components/ChatArea.tsx

import { useState, useRef, useEffect } from 'react';
import { useAppStore } from '../store/useAppStore';
import api from '../api/client';
import type { ChatResponse } from '../types';
import PerformanceChip from './PerformanceChip';
import SourceCard from './SourceCard';
import WelcomeBox from './WelcomeBox';
import QuickActions from './QuickActions';
import TipNote from './TipNote';

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
    addSecurityEvent,
  } = useAppStore();

  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // --- Refactored handleSend to accept a custom query ---
  const handleSend = async (customQuery?: string) => {
    const queryToSend = customQuery ?? input;
    if (!queryToSend.trim() || isLoading) return;

    // If custom query was used, clear input; otherwise keep it cleared
    if (customQuery) {
      setInput('');
    } else {
      setInput('');
    }

    const userMsg = { role: 'user' as const, content: queryToSend };
    addMessage(userMsg);
    setIsLoading(true);
    setChatResult([], null);

    try {
      const response = await api.post<ChatResponse>('/chat', {
        query: queryToSend,
        department,
        role,
        top_k: 5,
      });

      const data = response.data;

      if (data.security_warning && data.security_warning.blocked) {
        addMessage({
          role: 'assistant' as const,
          content: `⛔ ${data.security_warning.message}`,
          isWarning: true,
        });

        addSecurityEvent({
          timestamp: new Date().toISOString(),
          query: queryToSend,
          department,
          role,
          reason: data.security_warning.message,
          category: data.security_warning.category,
          risk_score: data.security_warning.risk_score,
          action_taken: 'block',
        });

        if (data.performance) {
          setChatResult([], data.performance);
        }
        return;
      }

      addMessage({ role: 'assistant' as const, content: data.answer || '' });
      setChatResult(data.sources, data.performance);

      addRequestLog({
        timestamp: new Date().toISOString(),
        query: queryToSend,
        department,
        role,
        latency_ms: data.performance?.latency_ms || 0,
        source_count: data.sources?.length || 0,
        status: 'success',
      });
    } catch (error) {
      addMessage({
        role: 'assistant' as const,
        content: 'Sorry, an error occurred. Please try again.',
      });

      addRequestLog({
        timestamp: new Date().toISOString(),
        query: queryToSend,
        department,
        role,
        latency_ms: 0,
        source_count: 0,
        status: 'error',
      });

      console.error('Chat error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col bg-white dark:bg-gray-900 h-full">
      {/* Header */}
      <div className="border-b border-gray-200 dark:border-gray-700 px-6 py-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-200">
          🗂️ {department} / {role}
        </h2>
        {performance && <PerformanceChip performance={performance} />}
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center min-h-[60vh]">
            <WelcomeBox />
            <QuickActions onSend={handleSend} />
            <TipNote />
          </div>
        ) : (
          <>
            {messages.map((msg, idx) => {
              let bubbleClasses = 'max-w-3xl rounded-lg px-4 py-3 ';
              if (msg.isWarning) {
                bubbleClasses += 'bg-yellow-50 border border-yellow-300 text-yellow-800 dark:bg-yellow-900/30 dark:border-yellow-700 dark:text-yellow-200';
              } else if (msg.role === 'user') {
                bubbleClasses += 'bg-primary-600 text-white';
              } else {
                bubbleClasses += 'bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200';
              }

              return (
                <div
                  key={idx}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div className={bubbleClasses}>
                    <p className="whitespace-pre-wrap">{msg.content}</p>
                    {msg.isWarning && (
                      <p className="text-xs text-yellow-600 dark:text-yellow-400 mt-1">
                        This attempt has been logged for security monitoring.
                      </p>
                    )}
                  </div>
                </div>
              );
            })}

            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-gray-100 dark:bg-gray-800 rounded-lg px-4 py-3 text-gray-500 dark:text-gray-400">
                  <span className="animate-pulse">▸</span> Thinking...
                </div>
              </div>
            )}

            {!isLoading && sources.length > 0 && (
              <div className="mt-4">
                <details className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden bg-gray-50 dark:bg-gray-800/50">
                  <summary className="px-4 py-3 font-medium text-gray-700 dark:text-gray-300 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700/50 transition flex items-center justify-between">
                    <span>📚 {sources.length} Sources Retrieved</span>
                    <span className="text-xs text-gray-400">Click to expand</span>
                  </summary>
                  <div className="p-4 space-y-3 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900">
                    {sources.map((source, idx) => (
                      <SourceCard key={idx} source={source} index={idx} />
                    ))}
                  </div>
                </details>
              </div>
            )}

            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-200 dark:border-gray-700 px-6 py-4 bg-white dark:bg-gray-900">
        <div className="flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask a question about your documents..."
            className="flex-1 border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition disabled:bg-gray-100 dark:disabled:bg-gray-800 dark:bg-gray-800 dark:text-gray-200"
            disabled={isLoading}
          />
          <button
            onClick={() => handleSend()}
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