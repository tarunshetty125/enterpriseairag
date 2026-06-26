"use client";

import { useEffect, useMemo, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { BarChart3, Target } from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { PageHeader } from "@/components/layout/page-header";
import { formatNumber, formatPercent, getRecordMetric } from "@/components/ml/format";
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
  getCustomers,
  getMLEvaluation,
  getMLModels,
  predictSegment,
} from "@/lib/api/platform";

export function SegmentationPanel() {
  const [customerId, setCustomerId] = useState("");
  const customers = useQuery({
    queryKey: ["customers", 100, 0],
    queryFn: () => getCustomers(100, 0),
  });
  const models = useQuery({
    queryKey: ["ml", "models"],
    queryFn: getMLModels,
  });
  const evaluation = useQuery({
    queryKey: ["ml", "evaluation"],
    queryFn: getMLEvaluation,
  });
  const prediction = useMutation({
    mutationFn: predictSegment,
  });
  const activeSegment = models.data?.models.find(
    (model) => model.modelName === "customer_segmentation" && model.activeModel,
  );
  const distribution = useMemo(() => {
    const source = getRecordMetric(evaluation.data?.segmentation ?? {}, "distribution");
    return Object.entries(source).map(([label, count]) => ({
      label,
      count: typeof count === "number" ? count : 0,
    }));
  }, [evaluation.data?.segmentation]);

  useEffect(() => {
    const firstCustomer = customers.data?.items[0]?.customerId;
    if (!customerId && firstCustomer) {
      setCustomerId(firstCustomer);
    }
  }, [customerId, customers.data?.items]);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Customer Segmentation"
        description="KMeans customer segmentation with business labels and centroid summaries."
      >
        <Badge variant="outline">
          {activeSegment ? `Active ${activeSegment.version}` : "No active model"}
        </Badge>
      </PageHeader>

      <div className="grid gap-4 xl:grid-cols-3">
        <Card className="xl:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-4 w-4" aria-hidden="true" />
              Segment Distribution
            </CardTitle>
            <CardDescription>
              Business labels generated from cluster centroids.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[320px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={distribution}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="label" tickLine={false} axisLine={false} />
                  <YAxis allowDecimals={false} tickLine={false} axisLine={false} />
                  <Tooltip />
                  <Bar
                    dataKey="count"
                    fill="hsl(var(--primary))"
                    radius={[4, 4, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Cluster Quality</CardTitle>
            <CardDescription>
              Evaluation metrics from active KMeans model.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Customers</span>
              <span>
                {formatNumber(activeSegment?.metrics.customer_count as number)}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Silhouette</span>
              <span>
                {formatNumber(activeSegment?.metrics.silhouette_score as number, 4)}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Davies Bouldin</span>
              <span>
                {formatNumber(activeSegment?.metrics.davies_bouldin_score as number, 4)}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Inertia</span>
              <span>{formatNumber(activeSegment?.metrics.inertia as number)}</span>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Predict Customer Segment</CardTitle>
          <CardDescription>
            Runs the active segmentation model for one customer.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-col gap-3 md:flex-row">
            <select
              className="h-9 rounded-md border bg-background px-3 text-sm"
              value={customerId}
              onChange={(event) => setCustomerId(event.target.value)}
            >
              {(customers.data?.items ?? []).map((customer) => (
                <option key={customer.customerId} value={customer.customerId}>
                  {customer.customerId} / {customer.fullName ?? "Unnamed"}
                </option>
              ))}
            </select>
            <Button
              disabled={!customerId || prediction.isPending}
              onClick={() => prediction.mutate(customerId)}
            >
              <Target className="h-4 w-4" aria-hidden="true" />
              Predict Segment
            </Button>
          </div>

          {prediction.data ? (
            <div className="grid gap-4 border-t pt-4 md:grid-cols-3">
              <div>
                <div className="text-sm text-muted-foreground">Business Label</div>
                <div className="mt-1 text-2xl font-semibold tracking-normal">
                  {prediction.data.segmentLabel}
                </div>
              </div>
              <div>
                <div className="text-sm text-muted-foreground">Confidence</div>
                <div className="mt-1 text-2xl font-semibold tracking-normal">
                  {formatPercent(prediction.data.confidence)}
                </div>
              </div>
              <div>
                <div className="text-sm text-muted-foreground">Distance</div>
                <div className="mt-1 text-2xl font-semibold tracking-normal">
                  {formatNumber(prediction.data.nearestDistance, 4)}
                </div>
              </div>
            </div>
          ) : null}
        </CardContent>
      </Card>
    </div>
  );
}
