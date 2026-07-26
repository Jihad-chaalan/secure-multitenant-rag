// src/components/TipNote.tsx

import { useAppStore } from '../store/useAppStore';

export default function TipNote() {
  const { messages } = useAppStore();

  // Only show when chat is empty (or keep it always visible — up to you)
  // I'll keep it always visible so they remember to switch contexts
  return (
    <div className="mt-4 flex items-start gap-2 bg-gray-50/80 dark:bg-gray-800/50 border border-gray-200/60 dark:border-gray-700/60 rounded-lg px-4 py-2.5 max-w-2xl mx-auto">
      <span className="text-sm text-gray-400 dark:text-gray-500 mt-0.5">💡</span>
      <p className="text-xs text-gray-500 dark:text-gray-400 leading-relaxed">
        <span className="font-medium">Tip:</span> Change the department and role in the sidebar to test different user perspectives.
        <br className="hidden sm:block" />
        Each role has tailored questions for RAG, security, and isolation testing.
      </p>
    </div>
  );
}