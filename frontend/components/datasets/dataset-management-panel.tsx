"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { RefreshCw } from "lucide-react";

import { StatusCard } from "@/components/dashboard/status-card";
import { PageHeader } from "@/components/layout/page-header";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  DataTable,
  DataTableBody,
  DataTableCell,
  DataTableHead,
  DataTableHeader,
  DataTableRow,
} from "@/components/ui/data-table";
import { getDatasetStatus, getDatasets, ingestDatasets } from "@/lib/api/platform";

export function DatasetManagementPanel() {
  const queryClient = useQueryClient();
  const datasets = useQuery({
    queryKey: ["datasets"],
    queryFn: getDatasets,
  });
  const status = useQuery({
    queryKey: ["datasets", "status"],
    queryFn: getDatasetStatus,
  });
  const ingest = useMutation({
    mutationFn: ingestDatasets,
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["datasets"] }),
        queryClient.invalidateQueries({ queryKey: ["platform"] }),
      ]);
    },
  });

  return (
    <div className="space-y-6">
      <PageHeader
        title="Dataset Management"
        description="Load, validate, normalize, and store public financial datasets in the canonical schema."
      >
        <Button onClick={() => ingest.mutate()} disabled={ingest.isPending}>
          <RefreshCw className="h-4 w-4" aria-hidden="true" />
          {ingest.isPending ? "Ingesting" : "Run Ingestion"}
        </Button>
      </PageHeader>
      <div className="grid gap-4 md:grid-cols-4">
        <StatusCard
          title="Configured"
          value={status.data?.configuredDatasets ?? 0}
          detail="Public datasets"
        />
        <StatusCard
          title="Loaded"
          value={status.data?.loadedDatasets ?? 0}
          detail="Metadata records"
        />
        <StatusCard
          title="Rows Loaded"
          value={status.data?.rowsLoaded ?? 0}
          detail="Source CSV rows"
        />
        <StatusCard
          title="SQLite Size"
          value={`${Math.round((status.data?.sqliteSizeBytes ?? 0) / 1024)} KB`}
          detail="Local database"
        />
      </div>
      {ingest.data ? (
        <Card>
          <CardHeader>
            <CardTitle>Latest Ingestion Result</CardTitle>
            <CardDescription>
              Generated {ingest.data.featureSnapshotsGenerated} feature snapshots with
              quality score {ingest.data.qualityScore}.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <DataTable>
              <DataTableHeader>
                <DataTableRow>
                  <DataTableHead>Dataset</DataTableHead>
                  <DataTableHead>Status</DataTableHead>
                  <DataTableHead>Rows</DataTableHead>
                  <DataTableHead>Message</DataTableHead>
                </DataTableRow>
              </DataTableHeader>
              <DataTableBody>
                {ingest.data.datasets.map((item) => (
                  <DataTableRow key={item.datasetName}>
                    <DataTableCell>{item.datasetName}</DataTableCell>
                    <DataTableCell>{item.status}</DataTableCell>
                    <DataTableCell>{item.rowsProcessed}</DataTableCell>
                    <DataTableCell>{item.message}</DataTableCell>
                  </DataTableRow>
                ))}
              </DataTableBody>
            </DataTable>
          </CardContent>
        </Card>
      ) : null}
      <Card>
        <CardHeader>
          <CardTitle>Dataset Metadata</CardTitle>
          <CardDescription>
            Metadata is populated only after successful ingestion.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <DataTable>
            <DataTableHeader>
              <DataTableRow>
                <DataTableHead>Name</DataTableHead>
                <DataTableHead>Status</DataTableHead>
                <DataTableHead>Rows</DataTableHead>
                <DataTableHead>Version</DataTableHead>
                <DataTableHead>Imported</DataTableHead>
              </DataTableRow>
            </DataTableHeader>
            <DataTableBody>
              {(datasets.data ?? []).map((dataset) => (
                <DataTableRow key={dataset.datasetName}>
                  <DataTableCell>{dataset.datasetName}</DataTableCell>
                  <DataTableCell>{dataset.status}</DataTableCell>
                  <DataTableCell>{dataset.rows}</DataTableCell>
                  <DataTableCell>{dataset.version}</DataTableCell>
                  <DataTableCell>
                    {new Date(dataset.importedAt).toLocaleString()}
                  </DataTableCell>
                </DataTableRow>
              ))}
            </DataTableBody>
          </DataTable>
        </CardContent>
      </Card>
    </div>
  );
}
