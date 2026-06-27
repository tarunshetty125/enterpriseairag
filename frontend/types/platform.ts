export interface HealthResponse {
  status: string;
  application: string;
  version: string;
  environment: string;
  timestamp: string;
}

export interface ComponentHealth {
  name: string;
  status: string;
  details: string;
}

export interface SystemHealthResponse {
  status: string;
  application: string;
  version: string;
  environment: string;
  components: ComponentHealth[];
  timestamp: string;
}

export interface AIProcessingSettings {
  provider: string;
  model: string;
  temperature: number;
  topP: number;
  topK: number;
  maxTokens: number;
  chunkSize: number;
  embeddingModel: string;
  conversationMemory: boolean;
}

export interface DatasetMetadata {
  datasetName: string;
  source: string;
  version: string;
  rows: number;
  columns: string[];
  importedAt: string;
  checksum: string;
  status: string;
}

export interface IngestionRun {
  id: number;
  datasetName: string;
  startedAt: string;
  finishedAt: string | null;
  status: string;
  rowsProcessed: number;
  message: string | null;
}

export interface FeatureStoreStatus {
  featureVersion: string;
  datasetVersion: string;
  snapshotCount: number;
  customerCount: number;
  latestGeneratedAt: string | null;
  featureCount: number;
  coverage: number;
}

export interface DatasetStatus {
  configuredDatasets: number;
  loadedDatasets: number;
  rowsLoaded: number;
  sqlitePath: string;
  sqliteSizeBytes: number;
  latestIngestion: IngestionRun | null;
  tableCounts: Record<string, number>;
  qualityScore: number;
  featureStore: FeatureStoreStatus;
}

export interface IngestionSummary {
  datasetName: string;
  status: string;
  rowsProcessed: number;
  checksum: string;
  startedAt: string;
  finishedAt: string;
  message: string;
}

export interface IngestionResponse {
  status: string;
  datasets: IngestionSummary[];
  featureSnapshotsGenerated: number;
  qualityScore: number;
}

export interface CustomerListItem {
  customerId: string;
  fullName: string | null;
  gender: string | null;
  age: number | null;
  geography: string | null;
  incomeCategory: string | null;
  estimatedIncome: number | null;
  creditScore: number | null;
  sourceDataset: string;
}

export interface CustomerListResponse {
  total: number;
  items: CustomerListItem[];
}

export interface Loan {
  id: number;
  loanType: string;
  amount: number;
  termMonths: number | null;
  status: string;
  creditHistory: number | null;
  propertyArea: string | null;
}

export interface Product {
  id: number;
  productType: string;
  status: string;
  creditLimit: number | null;
  revolvingBalance: number | null;
  revenue: number;
}

export interface Transaction {
  id: number;
  step: number | null;
  transactionType: string;
  category: string;
  direction: string;
  amount: number;
  description: string;
  counterparty: string | null;
  isFraud: number;
}

export interface FeatureItem {
  name: string;
  value: unknown;
  description: string;
  version: string;
  datasetVersion: string;
  generatedAt: string;
}

export interface CustomerFeatures {
  customerId: string;
  features: FeatureItem[];
}

export interface CustomerDetail extends CustomerListItem {
  education: string | null;
  maritalStatus: string | null;
  savingsBalance: number | null;
  tenureMonths: number | null;
  externalReferences: Record<string, unknown>;
  loans: Loan[];
  transactions: Transaction[];
  products: Product[];
  features: FeatureItem[];
}

export interface QualityCheck {
  name: string;
  status: string;
  affectedRows: number;
  details: string;
}

export interface QualityReport {
  score: number;
  checks: QualityCheck[];
}

export interface ModelRegistryItem {
  id: number;
  modelName: string;
  version: string;
  algorithm: string;
  trainingDate: string;
  metrics: Record<string, unknown>;
  accuracy: number | null;
  precision: number | null;
  recall: number | null;
  f1: number | null;
  featuresUsed: string[];
  artifactPath: string;
  datasetVersion: string;
  featureVersion: string;
  activeModel: boolean;
  trainingTimeMs: number;
  inferenceTimeMs: number | null;
  trainingMetadata: Record<string, unknown>;
  predictionCount: number;
}

export interface ModelRegistryResponse {
  models: ModelRegistryItem[];
}

export interface TrainModelResponse {
  model: ModelRegistryItem;
  message: string;
}

export interface FeatureContribution {
  name: string;
  value: number | string | null;
  importance: number;
  description: string;
}

export interface RiskPredictionResponse {
  customerId: string;
  riskLevel: string;
  confidence: number;
  probabilities: Record<string, number>;
  topFeatures: FeatureContribution[];
  businessExplanation: string;
  modelVersion: string;
  inferenceTimeMs: number;
}

export interface SegmentPredictionResponse {
  customerId: string;
  segmentLabel: string;
  confidence: number;
  nearestDistance: number;
  centroidSummary: Record<string, number>;
  modelVersion: string;
  inferenceTimeMs: number;
}

export interface MLEvaluationResponse {
  risk: Record<string, unknown> | null;
  segmentation: Record<string, unknown> | null;
}

export interface FeatureImportanceResponse {
  modelName: string;
  modelVersion: string;
  features: FeatureContribution[];
}

export interface TransactionInsight {
  id: number;
  transactionId: number;
  customerId: string;
  amount: number;
  direction: string;
  transactionType: string;
  rawDescription: string;
  category: string;
  keywords: string[];
  entities: Record<string, unknown>;
  sentimentLabel: string;
  sentimentScore: number;
  lifestyleIndicators: string[];
  processedAt: string;
}

export interface TransactionInsightsResponse {
  customerId: string;
  total: number;
  insights: TransactionInsight[];
  categoryDistribution: Record<string, number>;
  spendingDistribution: Record<string, number>;
}

export interface BehaviourProfile {
  customerId: string;
  profileVersion: string;
  summary: string;
  flags: string[];
  lifestyleIndicators: string[];
  categorySpend: Record<string, number>;
  categoryCounts: Record<string, number>;
  monthlyTrends: Array<Record<string, unknown>>;
  topMerchants: Array<Record<string, unknown>>;
  features: Record<string, unknown>;
  processingTimeMs: number;
  generatedAt: string;
}

export interface RecommendationRule {
  id: number;
  ruleId: string;
  productName: string;
  description: string;
  conditions: Record<string, unknown>;
  baseScore: number;
  version: string;
  active: boolean;
}

export interface Recommendation {
  id: number;
  customerId: string;
  ruleId: string;
  productName: string;
  suitabilityScore: number;
  confidence: number;
  reason: string;
  supportingFeatures: Array<Record<string, unknown>>;
  businessExplanation: string;
  recommendationVersion: string;
  status: string;
  generatedAt: string;
}

export interface RecommendationHistory {
  id: number;
  customerId: string;
  recommendationId: number | null;
  action: string;
  details: Record<string, unknown>;
  createdAt: string;
}

export interface RecommendationListResponse {
  customerId: string;
  currentProducts: Product[];
  recommendations: Recommendation[];
  history: RecommendationHistory[];
}

export interface RecommendationGenerationResponse {
  customerId: string;
  generated: number;
  recommendations: Recommendation[];
}

export interface IntelligenceStatusResponse {
  nlpProcessingVersion: string;
  transactionsProcessed: number;
  behaviourProfilesGenerated: number;
  averageNlpProcessingTimeMs: number;
  latestBehaviourProfileAt: string | null;
  recommendationRuleVersion: string;
  recommendationRuleCount: number;
  recommendationCount: number;
  recommendationHistoryCount: number;
  latestRecommendationAt: string | null;
}
