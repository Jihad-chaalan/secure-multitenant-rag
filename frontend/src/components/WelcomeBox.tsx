// src/components/WelcomeBox.tsx

export default function WelcomeBox() {
  return (
    <div className="max-w-3xl mx-auto mt-8 px-4 text-center animate-fade-in">
      {/* Title with Gradient */}
      <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight mb-3">
        <span className="bg-gradient-to-r from-blue-600 via-indigo-500 to-purple-600 bg-clip-text text-transparent">
          Secure Multi-Tenant RAG
        </span>
      </h1>

      {/* Subtitle */}
      <p className="text-gray-500 dark:text-gray-400 text-base sm:text-lg max-w-2xl mx-auto leading-relaxed">
        Production‑style AI knowledge assistant with hybrid retrieval, 
        <br className="hidden sm:block" />
        reranking, multi‑tenancy, and LLM security scanning.
      </p>

      {/* Architecture Flow Card */}
      <div className="mt-8 bg-white/70 dark:bg-gray-800/70 backdrop-blur-sm rounded-2xl border border-gray-200/80 dark:border-gray-700/80 shadow-xl shadow-gray-200/30 dark:shadow-gray-900/30 p-6 sm:p-8">
        <div className="flex items-center justify-center gap-1 sm:gap-4 flex-wrap">
          {/* Step 1 */}
          <Step icon="🧑‍💻" label="User" />
          <Arrow />
          
          {/* Step 2 */}
          <Step icon="🛡️" label="Scanner" />
          <Arrow />
          
          {/* Step 3 */}
          <Step icon="🔍" label="Hybrid" />
          <Arrow />
          
          {/* Step 4 */}
          <Step icon="🎯" label="Rerank" />
          <Arrow />
          
          {/* Step 5 */}
          <Step icon="🤖" label="LLM" />
          <Arrow />
          
          {/* Step 6 */}
          <Step icon="💬" label="Answer" />
        </div>

        {/* Tech Stack Description */}
        <div className="mt-5 pt-4 border-t border-gray-200/60 dark:border-gray-700/60 flex flex-wrap items-center justify-center gap-x-3 gap-y-1 text-[11px] font-mono text-gray-400 dark:text-gray-500">
          <span className="bg-gray-100 dark:bg-gray-800 px-2 py-0.5 rounded">AI Security Layer</span>
          <span className="text-gray-300 dark:text-gray-600">→</span>
          <span className="bg-gray-100 dark:bg-gray-800 px-2 py-0.5 rounded">BM25 + Vector</span>
          <span className="text-gray-300 dark:text-gray-600">→</span>
          <span className="bg-gray-100 dark:bg-gray-800 px-2 py-0.5 rounded">Cross-Encoder</span>
          <span className="text-gray-300 dark:text-gray-600">→</span>
          <span className="bg-gray-100 dark:bg-gray-800 px-2 py-0.5 rounded">Groq LLM</span>
        </div>
      </div>
    </div>
  );
}

// --- Helper Components for Cleaner Code ---

function Step({ icon, label }: { icon: string; label: string }) {
  return (
    <div className="flex flex-col items-center min-w-[48px] sm:min-w-[60px] group">
      <div className="text-2xl sm:text-3xl mb-1 transition-transform duration-200 group-hover:scale-110">
        {icon}
      </div>
      <span className="text-[10px] sm:text-xs font-medium text-gray-600 dark:text-gray-300 tracking-wide uppercase">
        {label}
      </span>
    </div>
  );
}

function Arrow() {
  return (
    <div className="text-gray-300 dark:text-gray-600 text-lg sm:text-xl font-light select-none">
      →
    </div>
  );
}