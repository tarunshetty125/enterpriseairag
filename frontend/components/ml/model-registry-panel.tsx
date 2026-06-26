"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Boxes, Brain, CheckCircle2, CirclePlay } from "lucide-react";

import { PageHeader } from "@/components/layout/page-header";
import { formatMs, formatPercent } from "@/components/ml/format";
import { Badge } from "@/components/ui/badge";
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
import {
  activateMLModel,
  getMLModels,
  trainRiskModel,
  trainSegmentationModel,
} from "@/lib/api/platform";

export function ModelRegistryPanel() {
  const queryClient = useQueryClient();
  const models = useQuery({
    queryKey: ["ml", "models"],
    queryFn: getMLModels,
  });

  const refresh = async () => {
    await queryClient.invalidateQueries({ queryKey: ["ml"] });
  };

  const trainRisk = useMutation({
    mutationFn: trainRiskModel,
    onSuccess: refresh,
  });

  const trainSegment = useMutation({
    mutationFn: trainSegmentationModel,
    onSuccess: refresh,
  });

  const activate = useMutation({
    mutationFn: activateMLModel,
    onSuccess: refresh,
  });

  return (
    <div className="space-y-6">
      <PageHeader
        title="Model Registry"
        description="Versioned local ML models with artifacts, metrics, feature versions, and active model state."
      />

      <div className="flex flex-col gap-3 sm:flex-row">
        <Button onClick={() => trainRisk.mutate()} disabled={trainRisk.isPending}>
          <Brain className="h-4 w-4" aria-hidden="true" />
          Train Risk Model
        </Button>
        <Button
          variant="outline"
          onClick={() => trainSegment.mutate()}
          disabled={trainSegment.isPending}
        >
          <Boxes className="h-4 w-4" aria-hidden="true" />
          Train Segmentation
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Registered Models</CardTitle>
          <CardDescription>
            {models.data?.models.length ?? 0} model versions registered.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <DataTable>
            <DataTableHeader>
              <DataTableRow>
                <DataTableHead>Model</DataTableHead>
                <DataTableHead>Algorithm</DataTableHead>
                <DataTableHead>Metrics</DataTableHead>
                <DataTableHead>Versions</DataTableHead>
                <DataTableHead>Runtime</DataTableHead>
                <DataTableHead>Status</DataTableHead>
              </DataTableRow>
            </DataTableHeader>
            <DataTableBody>
              {(models.data?.models ?? []).map((model) => (
                <DataTableRow key={model.id}>
                  <DataTableCell>
                    <div className="font-medium">{model.modelName}</div>
                    <div className="text-xs text-muted-foreground">{model.version}</div>
                  </DataTableCell>
                  <DataTableCell>{model.algorithm}</DataTableCell>
                  <DataTableCell>
                    <div>Accuracy {formatPercent(model.accuracy)}</div>
                    <div className="text-xs text-muted-foreground">
                      F1 {formatPercent(model.f1)}
                    </div>
                  </DataTableCell>
                  <DataTableCell>
                    <div className="text-xs">Dataset {model.datasetVersion}</div>
                    <div className="text-xs text-muted-foreground">
                      Feature {model.featureVersion}
                    </div>
                  </DataTableCell>
                  <DataTableCell>
                    <div>{formatMs(model.trainingTimeMs)}</div>
                    <div className="text-xs text-muted-foreground">
                      {model.predictionCount} predictions
                    </div>
                  </DataTableCell>
                  <DataTableCell>
                    {model.activeModel ? (
                      <Badge>
                        <CheckCircle2 className="mr-1 h-3 w-3" aria-hidden="true" />
                        Active
                      </Badge>
                    ) : (
                      <Button
                        size="sm"
                        variant="outline"
                        disabled={activate.isPending}
                        onClick={() => activate.mutate(model.id)}
                      >
                        <CirclePlay className="h-3.5 w-3.5" aria-hidden="true" />
                        Activate
                      </Button>
                    )}
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
