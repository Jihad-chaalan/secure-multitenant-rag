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
      } else if (data.status === "degraded") {
        setStatus("degraded");
        setLabel("Degraded");
      } else {
        setStatus("offline");
        setLabel("Offline");
      }
    } catch (error) {
      setStatus("offline");
      setLabel("Offline");
    }
  };

  useEffect(() => {
    let interval: number | null = null;  

    const startPolling = () => {
      if (interval) return;
      interval = window.setInterval(checkHealth, 30000);  
    };

    const stopPolling = () => {
      if (interval) {
        clearInterval(interval);
        interval = null;
      }
    };

    // Check once immediately
    checkHealth();

    // Start polling if tab is visible
    if (document.visibilityState === "visible") {
      startPolling();
    }

    const handleVisibilityChange = () => {
      if (document.visibilityState === "visible") {
        startPolling();
      } else {
        stopPolling();
      }
    };

    document.addEventListener("visibilitychange", handleVisibilityChange);

    return () => {
      stopPolling();
      document.removeEventListener("visibilitychange", handleVisibilityChange);
    };
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
      />
      <span className={`font-medium ${styles.text}`}>{label}</span>
    </div>
  );
}