import { apiClient, unwrap } from "@/lib/api/client";
import type {
  AIProcessingSettings,
  CustomerDetail,
  CustomerFeatures,
  CustomerListResponse,
  DatasetMetadata,
  DatasetStatus,
  FeatureStoreStatus,
  HealthResponse,
  IngestionResponse,
  QualityReport,
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

export function getDatasets(): Promise<DatasetMetadata[]> {
  return unwrap(apiClient.get<DatasetMetadata[]>("/datasets"));
}

export function ingestDatasets(): Promise<IngestionResponse> {
  return unwrap(apiClient.post<IngestionResponse>("/datasets/ingest"));
}

export function getDatasetStatus(): Promise<DatasetStatus> {
  return unwrap(apiClient.get<DatasetStatus>("/datasets/status"));
}

export function getCustomers(limit = 100, offset = 0): Promise<CustomerListResponse> {
  return unwrap(
    apiClient.get<CustomerListResponse>("/customers", {
      params: { limit, offset },
    }),
  );
}

export function getCustomer(customerId: string): Promise<CustomerDetail> {
  return unwrap(apiClient.get<CustomerDetail>(`/customers/${customerId}`));
}

export function getCustomerFeatures(customerId: string): Promise<CustomerFeatures> {
  return unwrap(apiClient.get<CustomerFeatures>(`/customers/${customerId}/features`));
}

export function getDataQuality(): Promise<QualityReport> {
  return unwrap(apiClient.get<QualityReport>("/data-quality"));
}

export function getFeatureStoreStatus(): Promise<FeatureStoreStatus> {
  return unwrap(apiClient.get<FeatureStoreStatus>("/feature-store/status"));
}
