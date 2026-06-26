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
