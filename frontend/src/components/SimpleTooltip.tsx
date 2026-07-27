// src/components/SimpleTooltip.tsx

import { useState } from 'react';
import type { ReactNode } from 'react'; 

interface SimpleTooltipProps {
  children: ReactNode;
  className?: string;
}

export default function SimpleTooltip({ children, className = '' }: SimpleTooltipProps) {
  const [isVisible, setIsVisible] = useState(false);

  return (
    <div
      className={`relative inline-flex items-center ${className}`}
      onMouseEnter={() => setIsVisible(true)}
      onMouseLeave={() => setIsVisible(false)}
    >
      <button
        className="w-5 h-5 rounded-full bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-300 text-xs font-bold flex items-center justify-center hover:bg-gray-300 dark:hover:bg-gray-600 transition"
        aria-label="More info"
      >
        i
      </button>

      {isVisible && (
        <div className="absolute top-full left-0 mt-2 w-80 p-4 bg-white dark:bg-gray-800 rounded-xl shadow-2xl border border-gray-200 dark:border-gray-700 z-50 text-left">
          {children}
        </div>
      )}
    </div>
  );
}