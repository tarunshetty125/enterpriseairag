import { apiClient, unwrap } from "@/lib/api/client";
import type {
  AIProcessingSettings,
  HealthResponse,
  SystemHealthResponse,
} from "@/types/platform";

export function getHealth(): Promise<HealthResponse> {
  return unwrap(apiClient.get<HealthResponse>("/health"));
}

export function getSystemHealth(): Promise<SystemHealthResponse> {
  return unwrap(apiClient.get<SystemHealthResponse>("/system-health"));
}

export function getAIProcessingSettings(): Promise<AIProcessingSettings> {
  return unwrap(apiClient.get<AIProcessingSettings>("/settings/ai-processing"));
}
