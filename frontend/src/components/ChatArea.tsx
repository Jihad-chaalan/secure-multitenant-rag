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
import SkeletonLoader from './SkeletonLoader';
import { useTypingEffect } from '../hooks/useTypingEffect';

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

  // --- Typing Animation State ---
  const [streamingAnswer, setStreamingAnswer] = useState('');
  const [isTypingActive, setIsTypingActive] = useState(false);
  const { displayedText, isComplete } = useTypingEffect(streamingAnswer, 15);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, displayedText, isTypingActive]);

  // --- When typing finishes, save the message and show sources ---
  useEffect(() => {
    if (isComplete && streamingAnswer) {
      // Save the final answer to Zustand
      addMessage({
        role: 'assistant',
        content: streamingAnswer,
      });

      setStreamingAnswer('');

      // The sources and performance are already set in the API response handler
      // We just need to show them now.
      // Wait for the next render to show sources (they are already in the store)
      setIsTypingActive(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isComplete, streamingAnswer]);

  // --- Reset typing when a new query is sent ---
  const resetTyping = () => {
    setStreamingAnswer('');
    setIsTypingActive(false);
    setChatResult([], null);
  };

  const handleSend = async (customQuery?: string) => {
    const queryToSend = customQuery ?? input;
    if (!queryToSend.trim() || isLoading) return;

    if (customQuery) setInput('');
    else setInput('');

    // Reset typing state
    resetTyping();

    // Add user message
    addMessage({
      role: 'user',
      content: queryToSend,
      department: department,
      tenantRole: role,
    });

    setIsLoading(true);

    try {
      const response = await api.post<ChatResponse>('/chat', {
        query: queryToSend,
        department,
        role,
        top_k: 5,
      });

      const data = response.data;

      // --- Security Block ---
      if (data.security_warning && data.security_warning.blocked) {
          const requestId = crypto.randomUUID ? crypto.randomUUID() : Date.now().toString();
        addMessage({
          role: 'assistant',
          content: `⛔ ${data.security_warning.message}`,
          isWarning: true,
        });

        addSecurityEvent({
          timestamp: new Date().toISOString(),
          request_id:requestId,
          query: queryToSend,
          department,
          role,
          reason: data.security_warning.message,
          category: data.security_warning.category,
          risk_score: data.security_warning.risk_score,
          action_taken: 'block',
        });

        if (data.performance) setChatResult([], data.performance);
        setIsLoading(false);
        return;
      }

      // --- Normal Flow: Start Typing Animation ---
      const answerText = data.answer || '';
      setStreamingAnswer(answerText);
      setIsTypingActive(true);

      // Store sources and performance for later (they will be shown when typing finishes)
      setChatResult(data.sources, data.performance);

      // Log performance
      addRequestLog({
        timestamp: new Date().toISOString(),
        query: queryToSend,
        department,
        role,
        latency_ms: data.performance?.latency_ms || 0,
        source_count: data.sources?.length || 0,
        status: 'success',
        total_tokens: data.performance?.total_tokens || 0,
        prompt_tokens: data.performance?.prompt_tokens || 0,        
        completion_tokens: data.performance?.completion_tokens || 0,
      });

    } catch (error) {
      addMessage({
        role: 'assistant',
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
   <div className="flex-1 flex flex-col bg-white dark:bg-gray-900 h-full w-full min-w-0">
      {/* Header */}
      <div className="border-b border-gray-200 dark:border-gray-700 px-6 py-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100">
          🗂️ {department} / {role}
        </h2>
        {performance && <PerformanceChip performance={performance} />}
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {messages.length === 0 && !isTypingActive && !streamingAnswer ? (
          <div className="flex flex-col items-center justify-center min-h-[60vh] px-4 sm:px-6">
            <WelcomeBox />
            <TipNote />
          </div>
        ) : (
          <>
            {/* Existing messages */}
            {messages.map((msg, idx) => {
              let bubbleClasses = 'max-w-3xl rounded-lg px-4 py-3 ';
              if (msg.isWarning) {
                bubbleClasses += 'bg-yellow-50 border border-yellow-300 text-yellow-800 dark:bg-yellow-900/30 dark:border-yellow-700 dark:text-yellow-200';
              } else if (msg.role === 'user') {
                bubbleClasses += 'bg-blue-600 text-white shadow-sm';
              } else {
                bubbleClasses += 'bg-gray-100 text-gray-800 dark:text-white';
              }

              return (
                <div
                  key={idx}
                  className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}
                >
                  {msg.role === 'user' && msg.department && msg.tenantRole && (
                    <span className="text-[10px] font-mono text-gray-400 dark:text-gray-500 mb-1 mr-1">
                      {msg.department} / {msg.tenantRole}
                    </span>
                  )}
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

            {/* 🔥 Loading Skeleton (instead of "Thinking...") */}
            {isLoading && (
              <div className="flex justify-start">
                <SkeletonLoader />
              </div>
            )}

            {/* 🔥 Typing Animation (Streaming answer) */}
            {isTypingActive && (
              <div className="flex justify-start">
                <div className="max-w-3xl rounded-lg px-4 py-3 bg-gray-100 text-gray-800 dark:text-white dark:bg-gray-800">
                  <p className="whitespace-pre-wrap">{displayedText}</p>
                  <span className="inline-block w-1.5 h-4 bg-gray-400 dark:bg-gray-500 animate-pulse ml-0.5" />
                </div>
              </div>
            )}

            {/* 🔥 Sources (only shown after typing is complete) */}
            {!isLoading &&
             !isTypingActive &&
             !streamingAnswer &&
             sources.length > 0 && (
              <div className="mt-4">
                <details className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden bg-gray-50 dark:bg-gray-800/50">
                  <summary className="px-4 py-3 font-medium text-gray-700 dark:text-gray-200 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700/50 transition flex items-center justify-between">
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

      {/* QuickActions — Always visible */}
      <div className="px-6 py-3 border-t border-gray-100 dark:border-gray-800 bg-gray-50/50 dark:bg-gray-900/50">
        <QuickActions onSend={handleSend} />
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
            disabled={isLoading || isTypingActive}
          />
          <button
            onClick={() => handleSend()}
            disabled={isLoading || isTypingActive || !input.trim()}
            className="bg-blue-600 text-white px-6 py-2.5 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition font-medium"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}