// src/store/useAppStore.ts

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import type { Source, PerformanceMetrics, SecurityEvent } from '../types';

// ============================================================
// TYPES
// ============================================================

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

export interface Message {
  role: 'user' | 'assistant';
  content: string;
  isWarning?: boolean; // Optional flag for security warning messages
}



// ============================================================
// STATE INTERFACE
// ============================================================

interface AppState {
  // --- User Context ---
  department: string;
  role: string;

  // --- Chat ---
  messages: Message[];
  isLoading: boolean;

  // --- Chat Results ---
  sources: Source[];
  performance: PerformanceMetrics | null;

  // --- Admin ---
  isAdmin: boolean;

  // --- Logs ---
  requestHistory: RequestLog[];
  securityHistory: SecurityEvent[];

  // ==========================================================
  // ACTIONS
  // ==========================================================

  // Context
  setDepartment: (dept: string) => void;
  setRole: (role: string) => void;

  // Chat
  addMessage: (msg: Message) => void;
  setIsLoading: (loading: boolean) => void;
  setChatResult: (sources: Source[], performance: PerformanceMetrics | null) => void;
  clearMessages: () => void;

  // Admin
  toggleAdmin: () => void;

  // Request Logging (Performance)
  addRequestLog: (log: Omit<RequestLog, 'id'>) => void;
  clearHistory: () => void;

  // Security Logging (AI Firewall)
  addSecurityEvent: (event: Omit<SecurityEvent, 'id'>) => void;
  clearSecurityHistory: () => void;
}

// ============================================================
// STORE
// ============================================================

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      // --- Default State ---
      department: 'Department_A',
      role: 'Engineering',
      messages: [],
      isLoading: false,
      sources: [],
      performance: null,
      isAdmin: false,
      requestHistory: [],
      securityHistory: [],

      // --- Context Actions ---
      setDepartment: (dept) => set({ department: dept }),
      setRole: (role) => set({ role }),

      // --- Chat Actions ---
      addMessage: (msg) =>
        set((state) => ({
          messages: [...state.messages, msg],
        })),

      setIsLoading: (loading) => set({ isLoading: loading }),

      setChatResult: (sources, performance) =>
        set({ sources, performance }),

      clearMessages: () =>
        set({ messages: [], sources: [], performance: null }),

      // --- Admin Actions ---
      toggleAdmin: () =>
        set((state) => ({ isAdmin: !state.isAdmin })),

      // --- Request Logging (Performance) ---
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

      // --- Security Logging (AI Firewall) ---
      addSecurityEvent: (event) => {
        const newEvent = {
          ...event,
          id: crypto.randomUUID ? crypto.randomUUID() : Date.now().toString(),
        };
        set((state) => ({
          securityHistory: [newEvent, ...state.securityHistory],
        }));
      },

      clearSecurityHistory: () => set({ securityHistory: [] }),
    }),

    // --- Persistence Configuration ---
    {
      name: 'secure-rag-storage',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        // Only persist these fields
        department: state.department,
        role: state.role,
        messages: state.messages,
        requestHistory: state.requestHistory,
        securityHistory: state.securityHistory,
      }),
    }
  )
);