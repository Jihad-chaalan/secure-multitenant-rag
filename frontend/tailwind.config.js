/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  safelist: [
    // --- Force all dark classes used in your app ---
    "dark:bg-gray-900",
    "dark:bg-gray-800",
    "dark:bg-gray-700",
    "dark:bg-gray-50/80",
    "dark:bg-gray-800/50",
    "dark:bg-gray-900/50",
    "dark:bg-gray-800/70",
    "dark:text-gray-200",
    "dark:text-gray-300",
    "dark:text-gray-400",
    "dark:border-gray-700",
    "dark:border-gray-600",
    "dark:border-gray-800",
    "dark:hover:bg-gray-700",
    "dark:hover:bg-gray-600",
    "dark:hover:bg-gray-800",
    "dark:shadow-gray-900/30",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: "#eff6ff",
          100: "#dbeafe",
          500: "#3b82f6",
          600: "#2563eb",
          700: "#1d4ed8",
        },
      },
    },
  },
  plugins: [],
};
