"use client";

import { useQuery } from "@tanstack/react-query";

import {
  getAIProcessingSettings,
  getDataQuality,
  getDatasetStatus,
  getFeatureStoreStatus,
  getHealth,
  getIntelligenceStatus,
  getMLEvaluation,
  getMLModels,
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

  const datasetStatus = useQuery({
    queryKey: ["platform", "dataset-status"],
    queryFn: getDatasetStatus,
    refetchInterval: 30000,
  });

  const featureStoreStatus = useQuery({
    queryKey: ["platform", "feature-store-status"],
    queryFn: getFeatureStoreStatus,
    refetchInterval: 30000,
  });

  const dataQuality = useQuery({
    queryKey: ["platform", "data-quality"],
    queryFn: getDataQuality,
    refetchInterval: 30000,
  });

  const mlModels = useQuery({
    queryKey: ["platform", "ml-models"],
    queryFn: getMLModels,
    refetchInterval: 30000,
  });

  const mlEvaluation = useQuery({
    queryKey: ["platform", "ml-evaluation"],
    queryFn: getMLEvaluation,
    refetchInterval: 30000,
  });

  const intelligenceStatus = useQuery({
    queryKey: ["platform", "intelligence-status"],
    queryFn: getIntelligenceStatus,
    refetchInterval: 30000,
  });

  return {
    health,
    systemHealth,
    aiSettings,
    datasetStatus,
    featureStoreStatus,
    dataQuality,
    mlModels,
    mlEvaluation,
    intelligenceStatus,
  };
}
