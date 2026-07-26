// src/components/QuickActions.tsx

import { useAppStore } from '../store/useAppStore';
import { SAMPLE_QUESTIONS } from '../utils/constants';

interface QuickActionsProps {
  onSend: (query: string) => void;
}

export default function QuickActions({ onSend }: QuickActionsProps) {
  const { department, role, messages, isLoading } = useAppStore();

  // Only show if no messages yet
  if (messages.length > 0) return null;

  const questions = SAMPLE_QUESTIONS[department]?.[role];
  if (!questions) return null;

  const allQuestions = [
    ...questions.normal.map((q) => ({ text: q, type: 'normal' as const })),
    { text: questions.security, type: 'security' as const },
    { text: questions.cross_tenant, type: 'cross_tenant' as const },
  ];

  const getChipStyles = (type: 'normal' | 'security' | 'cross_tenant') => {
    switch (type) {
      case 'normal':
        return 'bg-blue-50 text-blue-700 border-blue-200 hover:bg-blue-100 dark:bg-blue-950/30 dark:text-blue-300 dark:border-blue-800 dark:hover:bg-blue-950/50';
      case 'security':
        return 'bg-red-50 text-red-700 border-red-200 hover:bg-red-100 dark:bg-red-950/30 dark:text-red-300 dark:border-red-800 dark:hover:bg-red-950/50';
      case 'cross_tenant':
        return 'bg-orange-50 text-orange-700 border-orange-200 hover:bg-orange-100 dark:bg-orange-950/30 dark:text-orange-300 dark:border-orange-800 dark:hover:bg-orange-950/50';
    }
  };

  const getIcon = (type: 'normal' | 'security' | 'cross_tenant') => {
    switch (type) {
      case 'normal':
        return '📄';
      case 'security':
        return '🧨';
      case 'cross_tenant':
        return '🔒';
    }
  };

  return (
    <div className="mt-6 space-y-3">
      {/* Description Text */}
      <p className="text-sm text-gray-500 dark:text-gray-400 text-center font-medium tracking-wide">
        ✦ Try these examples (click to ask) or write your question (you can check the drive link in the sidebar) ✦
      </p>

      {/* Chips Row */}
      <div className="flex flex-wrap items-center justify-center gap-2.5">
        {allQuestions.map((q, idx) => (
          <button
            key={idx}
            onClick={() => onSend(q.text)}
            disabled={isLoading}
            className={`
              px-4 py-2 rounded-full text-xs sm:text-sm font-medium border transition-all duration-200
              ${getChipStyles(q.type)}
              hover:shadow-md active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed
            `}
          >
            <span className="mr-1.5">{getIcon(q.type)}</span>
            {q.text.length > 60 ? q.text.slice(0, 60) + '…' : q.text}
          </button>
        ))}
      </div>

      {/* 🔥 NEW: Color Legend */}
      <div className="flex flex-wrap items-center justify-center gap-4 pt-1 text-xs text-gray-400 dark:text-gray-500">
        <span className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-full bg-blue-500"></span>
          Regular RAG
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-full bg-red-500"></span>
          Security (Prompt Injection)
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-full bg-orange-500"></span>
          Multi-Tenancy (Isolation)
        </span>
      </div>
    </div>
  );
}