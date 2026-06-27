"use client";

import {
  Activity,
  Brain,
  Database,
  Gauge,
  Layers3,
  Server,
  Settings2,
  ShieldCheck,
  Timer,
  Workflow,
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PageHeader } from "@/components/layout/page-header";
import { usePlatformStatus } from "@/hooks/use-platform-status";

function statusLabel(isSuccess: boolean, isLoading: boolean) {
  if (isLoading) {
    return "Checking";
  }
  return isSuccess ? "Online" : "Offline";
}

export function DeveloperConsolePanel() {
  const {
    health,
    systemHealth,
    aiSettings,
    datasetStatus,
    featureStoreStatus,
    dataQuality,
    intelligenceStatus,
    knowledgeStatus,
    mlModels,
    providerStatus,
  } = usePlatformStatus();
  const sqlite = systemHealth.data?.components.find((item) => item.name === "sqlite");
  const registeredModels = mlModels.data?.models ?? [];
  const latestModel = registeredModels[0];
  const activeModels = registeredModels.filter((model) => model.activeModel);
  const predictionCount = registeredModels.reduce(
    (total, model) => total + model.predictionCount,
    0,
  );
  const activeProvider = providerStatus.data?.providers.find((item) => item.active);
  const aiMetrics = providerStatus.data?.metrics ?? {};
  const metricValue = (key: string) => aiMetrics[key];

  const cards = [
    {
      label: "Backend Status",
      value: statusLabel(health.isSuccess, health.isLoading),
      detail: health.data?.application ?? health.error?.message ?? "Waiting for API",
      icon: Server,
    },
    {
      label: "SQLite Status",
      value:
        sqlite?.status ?? statusLabel(systemHealth.isSuccess, systemHealth.isLoading),
      detail: sqlite?.details ?? "Database health endpoint pending",
      icon: Database,
    },
    {
      label: "Current AI Provider",
      value: providerStatus.data?.settings.provider ?? aiSettings.data?.provider ?? "Unavailable",
      detail: activeProvider?.details ?? "Runtime provider manager",
      icon: Workflow,
    },
    {
      label: "Current Model",
      value: providerStatus.data?.settings.model ?? aiSettings.data?.model ?? "Unavailable",
      detail: `Provider status: ${activeProvider?.status ?? "unknown"}`,
      icon: Settings2,
    },
    {
      label: "Datasets",
      value: datasetStatus.data?.loadedDatasets ?? 0,
      detail: `${datasetStatus.data?.rowsLoaded ?? 0} rows loaded`,
      icon: Database,
    },
    {
      label: "Dataset Version",
      value: featureStoreStatus.data?.datasetVersion ?? "Unavailable",
      detail: "Derived from source checksums",
      icon: Layers3,
    },
    {
      label: "Feature Store",
      value: featureStoreStatus.data?.featureVersion ?? "Unavailable",
      detail: `${featureStoreStatus.data?.snapshotCount ?? 0} snapshots`,
      icon: Layers3,
    },
    {
      label: "Quality Score",
      value: dataQuality.data ? `${dataQuality.data.score.toFixed(1)}%` : "Unavailable",
      detail: `${dataQuality.data?.checks.length ?? 0} checks`,
      icon: ShieldCheck,
    },
    {
      label: "SQLite Size",
      value: `${Math.round((datasetStatus.data?.sqliteSizeBytes ?? 0) / 1024)} KB`,
      detail: datasetStatus.data?.sqlitePath ?? "Local SQLite database",
      icon: Database,
    },
    {
      label: "Latest Ingestion",
      value: datasetStatus.data?.latestIngestion?.status ?? "No runs",
      detail:
        datasetStatus.data?.latestIngestion?.message ??
        "Run ingestion from Dataset Management",
      icon: Server,
    },
    {
      label: "Registered Models",
      value: registeredModels.length,
      detail: `${activeModels.length} active models`,
      icon: Brain,
    },
    {
      label: "Latest Training",
      value: latestModel?.modelName ?? "No training",
      detail: latestModel
        ? new Date(latestModel.trainingDate).toLocaleString()
        : "Train from Model Registry",
      icon: Timer,
    },
    {
      label: "Training Time",
      value: latestModel
        ? `${latestModel.trainingTimeMs.toFixed(1)} ms`
        : "Unavailable",
      detail: latestModel?.version ?? "No model artifact",
      icon: Activity,
    },
    {
      label: "Inference Time",
      value: latestModel?.inferenceTimeMs
        ? `${latestModel.inferenceTimeMs.toFixed(1)} ms`
        : "Unavailable",
      detail: `${predictionCount} logged predictions`,
      icon: Gauge,
    },
    {
      label: "Model Health",
      value: activeModels.length >= 2 ? "Ready" : "Training needed",
      detail: "Risk and segmentation active model coverage",
      icon: ShieldCheck,
    },
    {
      label: "NLP Processing Time",
      value: intelligenceStatus.data
        ? `${intelligenceStatus.data.averageNlpProcessingTimeMs.toFixed(2)} ms`
        : "Unavailable",
      detail: intelligenceStatus.data?.nlpProcessingVersion ?? "No NLP runs",
      icon: Activity,
    },
    {
      label: "Transactions Processed",
      value: intelligenceStatus.data?.transactionsProcessed ?? 0,
      detail: `${intelligenceStatus.data?.behaviourProfilesGenerated ?? 0} behaviour profiles`,
      icon: Workflow,
    },
    {
      label: "Recommendations",
      value: intelligenceStatus.data?.recommendationCount ?? 0,
      detail: `${intelligenceStatus.data?.recommendationHistoryCount ?? 0} history events`,
      icon: Gauge,
    },
    {
      label: "Recommendation Rules",
      value: intelligenceStatus.data?.recommendationRuleCount ?? 0,
      detail: intelligenceStatus.data?.recommendationRuleVersion ?? "Rules not seeded",
      icon: Settings2,
    },
    {
      label: "Provider Health",
      value: activeProvider?.status ?? "Unavailable",
      detail: `${activeProvider?.latencyMs ?? 0} ms latency`,
      icon: Activity,
    },
    {
      label: "Token Usage",
      value: String(metricValue("total_tokens") ?? 0),
      detail: `${metricValue("metric_count") ?? 0} AI metric events`,
      icon: Gauge,
    },
    {
      label: "Embedding Model",
      value: knowledgeStatus.data?.embeddingBackend ?? "Unavailable",
      detail: knowledgeStatus.data?.embeddingModel ?? "No embeddings",
      icon: Brain,
    },
    {
      label: "FAISS Index Size",
      value: knowledgeStatus.data?.faissIndexSize ?? 0,
      detail: `${knowledgeStatus.data?.chunkCount ?? 0} knowledge chunks`,
      icon: Database,
    },
    {
      label: "Retrieved Chunks",
      value: String(metricValue("latest_retrieved_chunks") ?? 0),
      detail: `Context size ${metricValue("latest_context_size") ?? 0}`,
      icon: Layers3,
    },
    {
      label: "Provider Switches",
      value: providerStatus.data?.switchEvents.length ?? 0,
      detail: "Runtime switching events",
      icon: Workflow,
    },
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Developer Console"
        description="Operational view for backend health, SQLite, ML, NLP, AI Gateway, providers, RAG, and recommendations."
      >
        <Badge variant="outline">{health.data?.environment ?? "local"}</Badge>
      </PageHeader>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {cards.map((card) => {
          const Icon = card.icon;

          return (
            <Card key={card.label}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {card.label}
                </CardTitle>
                <Icon className="h-4 w-4 text-muted-foreground" aria-hidden="true" />
              </CardHeader>
              <CardContent className="space-y-2">
                <p className="text-xl font-semibold tracking-normal">{card.value}</p>
                <p className="text-xs text-muted-foreground">{card.detail}</p>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
