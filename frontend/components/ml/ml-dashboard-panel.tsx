"use client";

import { useQuery } from "@tanstack/react-query";
import { Activity, Brain, GitBranch, Timer } from "lucide-react";

import { PageHeader } from "@/components/layout/page-header";
import {
  formatMs,
  formatNumber,
  formatPercent,
  getNumberMetric,
} from "@/components/ml/format";
import { StatusCard } from "@/components/dashboard/status-card";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { getFeatureImportance, getMLEvaluation, getMLModels } from "@/lib/api/platform";

export function MLDashboardPanel() {
  const models = useQuery({
    queryKey: ["ml", "models"],
    queryFn: getMLModels,
  });
  const evaluation = useQuery({
    queryKey: ["ml", "evaluation"],
    queryFn: getMLEvaluation,
  });
  const activeRisk = models.data?.models.find(
    (model) => model.modelName === "risk_prediction" && model.activeModel,
  );
  const activeSegment = models.data?.models.find(
    (model) => model.modelName === "customer_segmentation" && model.activeModel,
  );
  const featureImportance = useQuery({
    queryKey: ["ml", "feature-importance", 8],
    queryFn: () => getFeatureImportance(8),
    enabled: Boolean(activeRisk),
  });
  const latestTraining = models.data?.models[0];
  const segmentationMetrics = evaluation.data?.segmentation ?? {};
  const activeModelCards = [activeRisk, activeSegment].flatMap((model) =>
    model ? [model] : [],
  );

  return (
    <div className="space-y-6">
      <PageHeader
        title="Machine Learning Dashboard"
        description="Phase 3 model training, evaluation, registry health, and explainability overview."
      >
        <Badge variant="outline">
          {models.data?.models.length ?? 0} registered models
        </Badge>
      </PageHeader>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatusCard
          title="Active Risk Model"
          value={activeRisk?.version ?? "Not trained"}
          detail={activeRisk ? activeRisk.algorithm : "Train from Model Registry"}
        />
        <StatusCard
          title="Risk Accuracy"
          value={formatPercent(activeRisk?.accuracy)}
          detail={`F1 ${formatPercent(activeRisk?.f1)}`}
        />
        <StatusCard
          title="Segmentation"
          value={activeSegment?.version ?? "Not trained"}
          detail={`${formatNumber(
            getNumberMetric(segmentationMetrics, "silhouette_score"),
            3,
          )} silhouette`}
        />
        <StatusCard
          title="Predictions"
          value={
            (models.data?.models ?? []).reduce(
              (total, model) => total + model.predictionCount,
              0,
            ) ?? 0
          }
          detail="Logged local inferences"
        />
      </div>

      <div className="grid gap-4 xl:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Brain className="h-4 w-4" aria-hidden="true" />
              Active Models
            </CardTitle>
            <CardDescription>Dataset and feature versions in use.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {activeModelCards.map((model) => (
              <div key={model.id} className="border-b pb-3 text-sm last:border-0">
                <div className="font-medium">{model.modelName}</div>
                <div className="mt-1 text-xs text-muted-foreground">
                  {model.version} / {model.featureVersion}
                </div>
                <div className="mt-2 text-xs text-muted-foreground">
                  Dataset {model.datasetVersion}
                </div>
              </div>
            ))}
            {!activeRisk && !activeSegment ? (
              <p className="text-sm text-muted-foreground">
                No active models yet. Train risk and segmentation models from the
                registry page.
              </p>
            ) : null}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-4 w-4" aria-hidden="true" />
              Evaluation
            </CardTitle>
            <CardDescription>
              Latest metrics from active registry entries.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">ROC AUC</span>
              <span>
                {formatNumber(getNumberMetric(activeRisk?.metrics ?? {}, "roc_auc"), 3)}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Precision</span>
              <span>{formatPercent(activeRisk?.precision)}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Recall</span>
              <span>{formatPercent(activeRisk?.recall)}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Training Time</span>
              <span>{formatMs(latestTraining?.trainingTimeMs)}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <GitBranch className="h-4 w-4" aria-hidden="true" />
              Feature Importance
            </CardTitle>
            <CardDescription>Top Random Forest drivers.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {(featureImportance.data?.features ?? []).map((feature) => (
              <div key={feature.name} className="space-y-1">
                <div className="flex items-center justify-between gap-3 text-xs">
                  <span>{feature.name.replaceAll("_", " ")}</span>
                  <span className="text-muted-foreground">
                    {formatNumber(feature.importance, 4)}
                  </span>
                </div>
                <div className="h-2 overflow-hidden rounded-full bg-muted">
                  <div
                    className="h-full rounded-full bg-primary"
                    style={{ width: `${Math.min(feature.importance * 100, 100)}%` }}
                  />
                </div>
              </div>
            ))}
            {!activeRisk ? (
              <p className="text-sm text-muted-foreground">
                Feature importance appears after training the risk model.
              </p>
            ) : null}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Timer className="h-4 w-4" aria-hidden="true" />
            Training Status
          </CardTitle>
          <CardDescription>
            Training is explicit and never runs automatically on startup.
          </CardDescription>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground">
          Latest training:{" "}
          {latestTraining
            ? `${latestTraining.modelName} at ${new Date(
                latestTraining.trainingDate,
              ).toLocaleString()}`
            : "No model training has been recorded."}
        </CardContent>
      </Card>
    </div>
  );
}
