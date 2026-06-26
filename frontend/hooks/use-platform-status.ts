"use client";

import { useQuery } from "@tanstack/react-query";

import {
  getAIProcessingSettings,
  getHealth,
  getSystemHealth,
} from "@/lib/api/platform";

export function usePlatformStatus() {
  const health = useQuery({
    queryKey: ["platform", "health"],
    queryFn: getHealth,
    refetchInterval: 30000,
  });

  const systemHealth = useQuery({
    queryKey: ["platform", "system-health"],
    queryFn: getSystemHealth,
    refetchInterval: 30000,
  });

  const aiSettings = useQuery({
    queryKey: ["platform", "ai-processing-settings"],
    queryFn: getAIProcessingSettings,
    refetchInterval: 30000,
  });

  return {
    health,
    systemHealth,
    aiSettings,
  };
}
