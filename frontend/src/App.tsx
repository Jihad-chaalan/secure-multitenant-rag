// src/App.tsx

import { BrowserRouter, Routes, Route } from "react-router-dom";
import UserPage from "./pages/UserPage";
import AdminPage from "./pages/AdminPage";
import Navbar from "./components/Navbar";

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors">
        <Navbar />
        <Routes>
          <Route path="/" element={<UserPage />} />
          <Route path="/admin" element={<AdminPage />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;