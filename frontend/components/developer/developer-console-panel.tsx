"use client";

import {
  Database,
  Layers3,
  Server,
  Settings2,
  ShieldCheck,
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
  } = usePlatformStatus();
  const sqlite = systemHealth.data?.components.find((item) => item.name === "sqlite");

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
      value: aiSettings.data?.provider ?? "Unavailable",
      detail: "Configuration only; no providers in Phase 2",
      icon: Workflow,
    },
    {
      label: "Current Model",
      value: aiSettings.data?.model ?? "Unavailable",
      detail: `Version ${health.data?.version ?? "unknown"}`,
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
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Developer Console"
        description="Phase 2 operational view for backend health, SQLite, datasets, feature store, and quality checks."
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
