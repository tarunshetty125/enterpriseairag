import { apiClient, unwrap } from "@/lib/api/client";
import type {
  AIProcessingSettings,
  CustomerDetail,
  CustomerFeatures,
  CustomerListResponse,
  DatasetMetadata,
  DatasetStatus,
  FeatureImportanceResponse,
  FeatureStoreStatus,
  HealthResponse,
  IngestionResponse,
  BehaviourProfile,
  IntelligenceStatusResponse,
  MLEvaluationResponse,
  ModelRegistryItem,
  ModelRegistryResponse,
  QualityReport,
  RecommendationGenerationResponse,
  RecommendationListResponse,
  RecommendationRule,
  RiskPredictionResponse,
  SegmentPredictionResponse,
  SystemHealthResponse,
  TransactionInsightsResponse,
  TrainModelResponse,
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

export function trainRiskModel(): Promise<TrainModelResponse> {
  return unwrap(apiClient.post<TrainModelResponse>("/ml/train/risk"));
}

export function trainSegmentationModel(): Promise<TrainModelResponse> {
  return unwrap(apiClient.post<TrainModelResponse>("/ml/train/segmentation"));
}

export function getMLModels(): Promise<ModelRegistryResponse> {
  return unwrap(apiClient.get<ModelRegistryResponse>("/ml/models"));
}

export function getMLModel(model: string): Promise<ModelRegistryItem> {
  return unwrap(apiClient.get<ModelRegistryItem>(`/ml/models/${model}`));
}

export function activateMLModel(modelId: number): Promise<ModelRegistryItem> {
  return unwrap(apiClient.post<ModelRegistryItem>(`/ml/models/${modelId}/activate`));
}

export function predictRisk(customerId: string): Promise<RiskPredictionResponse> {
  return unwrap(
    apiClient.post<RiskPredictionResponse>("/ml/predict/risk", {
      customerId,
    }),
  );
}

export function predictSegment(customerId: string): Promise<SegmentPredictionResponse> {
  return unwrap(
    apiClient.post<SegmentPredictionResponse>("/ml/predict/segment", {
      customerId,
    }),
  );
}

export function getMLEvaluation(): Promise<MLEvaluationResponse> {
  return unwrap(apiClient.get<MLEvaluationResponse>("/ml/evaluation"));
}

export function getFeatureImportance(limit = 10): Promise<FeatureImportanceResponse> {
  return unwrap(
    apiClient.get<FeatureImportanceResponse>("/ml/feature-importance", {
      params: { limit },
    }),
  );
}

export function getTransactionInsights(
  customerId: string,
): Promise<TransactionInsightsResponse> {
  return unwrap(
    apiClient.get<TransactionInsightsResponse>(
      `/transactions/${customerId}/insights`,
    ),
  );
}

export function getCustomerBehaviour(customerId: string): Promise<BehaviourProfile> {
  return unwrap(apiClient.get<BehaviourProfile>(`/customers/${customerId}/behaviour`));
}

export function generateRecommendations(
  customerId: string,
): Promise<RecommendationGenerationResponse> {
  return unwrap(
    apiClient.post<RecommendationGenerationResponse>(
      `/recommendations/generate/${customerId}`,
    ),
  );
}

export function getRecommendations(
  customerId: string,
): Promise<RecommendationListResponse> {
  return unwrap(
    apiClient.get<RecommendationListResponse>(`/recommendations/${customerId}`),
  );
}

export function getRecommendationRules(): Promise<RecommendationRule[]> {
  return unwrap(apiClient.get<RecommendationRule[]>("/recommendation-rules"));
}

export function getIntelligenceStatus(): Promise<IntelligenceStatusResponse> {
  return unwrap(apiClient.get<IntelligenceStatusResponse>("/intelligence/status"));
}
