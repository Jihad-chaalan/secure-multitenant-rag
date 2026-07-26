// src/components/SystemStatus.tsx

import { useEffect, useState } from "react";
import api from "../api/client";

type Status = "online" | "degraded" | "offline";

export default function SystemStatus() {
  const [status, setStatus] = useState<Status>("offline");
  const [label, setLabel] = useState("Checking...");

  const checkHealth = async () => {
    try {
      const response = await api.get("/health");
      const data = response.data;

      if (data.status === "healthy") {
        setStatus("online");
        setLabel("Online");
      } else {
        setStatus("degraded");
        setLabel("Degraded");
      }
    } catch (error) {
      setStatus("offline");
      setLabel("Offline");
    }
  };

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 30000); // Poll every 30s
    return () => clearInterval(interval);
  }, []);

  const getStyles = () => {
    switch (status) {
      case "online":
        return {
          dot: "bg-green-500",
          text: "text-green-600 dark:text-green-400",
        };
      case "degraded":
        return {
          dot: "bg-yellow-500",
          text: "text-yellow-600 dark:text-yellow-400",
        };
      default:
        return {
          dot: "bg-red-500",
          text: "text-red-600 dark:text-red-400",
        };
    }
  };

  const styles = getStyles();

  return (
    <div className="flex items-center gap-2 text-sm">
      <span
        className={`inline-block w-2.5 h-2.5 rounded-full ${styles.dot} animate-pulse`}
      ></span>
      <span className={`font-medium ${styles.text}`}>{label}</span>
    </div>
  );
}