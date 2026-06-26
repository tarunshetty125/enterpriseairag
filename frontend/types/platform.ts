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
