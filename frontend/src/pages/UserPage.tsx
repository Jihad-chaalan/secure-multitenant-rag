// src/pages/UserPage.tsx

import Sidebar from '../components/Sidebar';
import ChatArea from '../components/ChatArea';

export default function UserPage() {
  return (
    <div className="flex h-[calc(100vh-73px)]">
      <Sidebar />
      <ChatArea />
    </div>
  );
}