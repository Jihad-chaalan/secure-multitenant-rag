// src/components/SkeletonLoader.tsx

export default function SkeletonLoader() {
  return (
    <div className="max-w-3xl rounded-lg px-4 py-3 bg-gray-100 dark:bg-gray-800">
      {/* Shimmering text lines */}
      <div className="space-y-2.5">
        <div className="h-4 w-full rounded shimmer-bg"></div>
        <div className="h-4 w-3/4 rounded shimmer-bg"></div>
        <div className="h-4 w-1/2 rounded shimmer-bg"></div>
      </div>

      {/* Bouncing dots indicator */}
      <div className="flex items-center gap-1.5 mt-3">
        <span className="w-2 h-2 rounded-full bg-gray-400 dark:bg-gray-500 animate-bounce [animation-delay:-0.3s]"></span>
        <span className="w-2 h-2 rounded-full bg-gray-400 dark:bg-gray-500 animate-bounce [animation-delay:-0.15s]"></span>
        <span className="w-2 h-2 rounded-full bg-gray-400 dark:bg-gray-500 animate-bounce [animation-delay:0s]"></span>
        <span className="ml-1 text-xs text-gray-400 dark:text-gray-500 font-medium">Thinking</span>
      </div>
    </div>
  );
}