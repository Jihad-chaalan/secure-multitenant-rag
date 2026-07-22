// src/store/useAppStore.ts

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import type { Source, PerformanceMetrics } from '../types';

export interface RequestLog {
  id: string;
  timestamp: string;
  query: string;
  department: string;
  role: string;
  latency_ms: number;
  source_count: number;
  status: 'success' | 'error';
}

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface AppState {
  // User Context
  department: string;
  role: string;
  messages: Message[];
  isLoading: boolean;
  // Chat Results
  sources: Source[];
  performance: PerformanceMetrics | null;
  // Admin Context
  isAdmin: boolean;
  // Request History (for Admin Dashboard)
  requestHistory: RequestLog[];

  // Actions
  setDepartment: (dept: string) => void;
  setRole: (role: string) => void;
  addMessage: (msg: Message) => void;
  setIsLoading: (loading: boolean) => void;
  setChatResult: (sources: Source[], performance: PerformanceMetrics | null) => void;
  clearMessages: () => void;
  toggleAdmin: () => void;
  addRequestLog: (log: Omit<RequestLog, 'id'>) => void;
  clearHistory: () => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      department: 'Department_A',
      role: 'Engineering',
      messages: [],
      isLoading: false,
      sources: [],
      performance: null,
      isAdmin: false,
      requestHistory: [],

      setDepartment: (dept) => set({ department: dept }),
      setRole: (role) => set({ role }),
      addMessage: (msg) => set((state) => ({ messages: [...state.messages, msg] })),
      setIsLoading: (loading) => set({ isLoading: loading }),
      setChatResult: (sources, performance) => set({ sources, performance }),
      clearMessages: () => set({ messages: [], sources: [], performance: null }),
      toggleAdmin: () => set((state) => ({ isAdmin: !state.isAdmin })),

      addRequestLog: (log) => {
        const newLog = {
          ...log,
          id: crypto.randomUUID ? crypto.randomUUID() : Date.now().toString(),
        };
        set((state) => ({
          requestHistory: [newLog, ...state.requestHistory],
        }));
      },

      clearHistory: () => set({ requestHistory: [] }),
    }),
    {
      name: 'secure-rag-storage', // key in localStorage
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        department: state.department,
        role: state.role,
        messages: state.messages,
        requestHistory: state.requestHistory,
      }),
    }
  )
);