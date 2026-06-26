"use client";

import { useQuery } from "@tanstack/react-query";

import { StatusCard } from "@/components/dashboard/status-card";
import { PageHeader } from "@/components/layout/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  DataTable,
  DataTableBody,
  DataTableCell,
  DataTableHead,
  DataTableHeader,
  DataTableRow,
} from "@/components/ui/data-table";
import { getDataQuality, getDatasets } from "@/lib/api/platform";

export function DataQualityPanel() {
  const quality = useQuery({
    queryKey: ["data-quality"],
    queryFn: getDataQuality,
  });
  const datasets = useQuery({
    queryKey: ["datasets"],
    queryFn: getDatasets,
  });

  return (
    <div className="space-y-6">
      <PageHeader
        title="Data Quality"
        description="Deterministic validation checks over the canonical financial schema."
      />
      <div className="grid gap-4 md:grid-cols-3">
        <StatusCard
          title="Quality Score"
          value={quality.data ? `${quality.data.score.toFixed(1)}%` : "Unavailable"}
          detail="Current canonical dataset"
        />
        <StatusCard
          title="Datasets"
          value={datasets.data?.length ?? 0}
          detail="Loaded metadata rows"
        />
        <StatusCard
          title="Validation Checks"
          value={quality.data?.checks.length ?? 0}
          detail="Phase 2 rule set"
        />
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Validation Results</CardTitle>
        </CardHeader>
        <CardContent>
          <DataTable>
            <DataTableHeader>
              <DataTableRow>
                <DataTableHead>Check</DataTableHead>
                <DataTableHead>Status</DataTableHead>
                <DataTableHead>Affected Rows</DataTableHead>
                <DataTableHead>Details</DataTableHead>
              </DataTableRow>
            </DataTableHeader>
            <DataTableBody>
              {(quality.data?.checks ?? []).map((check) => (
                <DataTableRow key={check.name}>
                  <DataTableCell>{check.name}</DataTableCell>
                  <DataTableCell>{check.status}</DataTableCell>
                  <DataTableCell>{check.affectedRows}</DataTableCell>
                  <DataTableCell>{check.details}</DataTableCell>
                </DataTableRow>
              ))}
            </DataTableBody>
          </DataTable>
        </CardContent>
      </Card>
    </div>
  );
}
