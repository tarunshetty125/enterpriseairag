"use client";

import { PageHeader } from "@/components/layout/page-header";
import { StatusCard } from "@/components/dashboard/status-card";
import { usePlatformStatus } from "@/hooks/use-platform-status";

export function DashboardPanel() {
  const { datasetStatus, featureStoreStatus, dataQuality, health } =
    usePlatformStatus();

  return (
    <div className="space-y-6">
      <PageHeader
        title="Dashboard"
        description="Phase 2 operational overview for the canonical data foundation."
      />
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatusCard
          title="Backend"
          value={health.data?.status ?? "Checking"}
          detail={health.data?.version ? `Version ${health.data.version}` : undefined}
        />
        <StatusCard
          title="Datasets Loaded"
          value={datasetStatus.data?.loadedDatasets ?? 0}
          detail={`${datasetStatus.data?.rowsLoaded ?? 0} source rows`}
        />
        <StatusCard
          title="Feature Snapshots"
          value={featureStoreStatus.data?.snapshotCount ?? 0}
          detail={`${featureStoreStatus.data?.featureCount ?? 0} engineered features`}
        />
        <StatusCard
          title="Quality Score"
          value={
            dataQuality.data ? `${dataQuality.data.score.toFixed(1)}%` : "Unavailable"
          }
          detail="Deterministic data checks"
        />
      </div>
    </div>
  );
}
