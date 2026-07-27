// src/components/Sidebar.tsx

import SidebarContent from "./SidebarContent";

export default function Sidebar() {
  return (
    <aside className="hidden lg:flex w-80 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700 flex-col h-full shadow-sm">
      <SidebarContent />
    </aside>
  );
}