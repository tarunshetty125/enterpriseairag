"use client";

import { useEffect, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Sparkles } from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { StatusCard } from "@/components/dashboard/status-card";
import { PageHeader } from "@/components/layout/page-header";
import { formatNumber, formatPercent } from "@/components/ml/format";
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
  generateRecommendations,
  getCustomers,
  getRecommendationRules,
  getRecommendations,
} from "@/lib/api/platform";
import type { Recommendation } from "@/types/platform";

function featureLabel(feature: Record<string, unknown>) {
  const name = String(feature.name ?? "Feature");
  const value = feature.value;
  const impact = typeof feature.impact === "number" ? feature.impact : 0;
  return `${name}: ${String(value)} (${impact > 0 ? "+" : ""}${impact})`;
}

export function RecommendationDashboardPanel() {
  const [customerId, setCustomerId] = useState("");
  const queryClient = useQueryClient();
  const customers = useQuery({
    queryKey: ["customers", 200, 0],
    queryFn: () => getCustomers(200, 0),
  });
  const recommendations = useQuery({
    queryKey: ["recommendations", customerId],
    queryFn: () => getRecommendations(customerId),
    enabled: Boolean(customerId),
  });
  const rules = useQuery({
    queryKey: ["recommendation-rules"],
    queryFn: getRecommendationRules,
  });
  const generation = useMutation({
    mutationFn: generateRecommendations,
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: ["recommendations", customerId],
      });
      await queryClient.invalidateQueries({
        queryKey: ["platform", "intelligence-status"],
      });
    },
  });
  const scoreData = useMemo(
    () =>
      (recommendations.data?.recommendations ?? []).map(
        (recommendation: Recommendation) => ({
          product: recommendation.productName,
          score: recommendation.suitabilityScore,
        }),
      ),
    [recommendations.data?.recommendations],
  );

  useEffect(() => {
    const firstCustomer = customers.data?.items[0]?.customerId;
    if (!customerId && firstCustomer) {
      setCustomerId(firstCustomer);
    }
  }, [customerId, customers.data?.items]);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Recommendations"
        description="Rules-based explainable product recommendations from features, ML outputs, and behavioural profiles."
      >
        <Badge variant="outline">{rules.data?.[0]?.version ?? "Rule catalog"}</Badge>
      </PageHeader>

      <Card>
        <CardHeader>
          <CardTitle>Recommendation Explorer</CardTitle>
          <CardDescription>
            Generate deterministic recommendations for a selected customer.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-3 md:flex-row">
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
            disabled={!customerId || generation.isPending}
            onClick={() => generation.mutate(customerId)}
          >
            <Sparkles className="h-4 w-4" aria-hidden="true" />
            Generate
          </Button>
        </CardContent>
      </Card>

      <div className="grid gap-4 md:grid-cols-4">
        <StatusCard
          title="Recommendations"
          value={recommendations.data?.recommendations.length ?? 0}
        />
        <StatusCard title="Active Rules" value={rules.data?.length ?? 0} />
        <StatusCard
          title="Current Products"
          value={recommendations.data?.currentProducts.length ?? 0}
        />
        <StatusCard
          title="History Events"
          value={recommendations.data?.history.length ?? 0}
        />
      </div>

      <div className="grid gap-6 xl:grid-cols-3">
        <Card className="xl:col-span-2">
          <CardHeader>
            <CardTitle>Suitability Scores</CardTitle>
            <CardDescription>Score assigned by the deterministic rules engine.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[320px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={scoreData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="product" tickLine={false} axisLine={false} />
                  <YAxis domain={[0, 100]} tickLine={false} axisLine={false} />
                  <Tooltip />
                  <Bar
                    dataKey="score"
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
            <CardTitle>Current Products</CardTitle>
            <CardDescription>Existing active products for this customer.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            {(recommendations.data?.currentProducts ?? []).map((product) => (
              <div
                key={product.id}
                className="flex items-center justify-between rounded-md border p-3 text-sm"
              >
                <span>{product.productType}</span>
                <Badge variant="outline">{product.status}</Badge>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Recommended Products</CardTitle>
          <CardDescription>Reasons and supporting factors are persisted with each result.</CardDescription>
        </CardHeader>
        <CardContent>
          <DataTable>
            <DataTableHeader>
              <DataTableRow>
                <DataTableHead>Product</DataTableHead>
                <DataTableHead>Score</DataTableHead>
                <DataTableHead>Confidence</DataTableHead>
                <DataTableHead>Reason</DataTableHead>
                <DataTableHead>Supporting Features</DataTableHead>
              </DataTableRow>
            </DataTableHeader>
            <DataTableBody>
              {(recommendations.data?.recommendations ?? []).map((recommendation) => (
                <DataTableRow key={recommendation.id}>
                  <DataTableCell>{recommendation.productName}</DataTableCell>
                  <DataTableCell>
                    {formatNumber(recommendation.suitabilityScore)}
                  </DataTableCell>
                  <DataTableCell>
                    {formatPercent(recommendation.confidence)}
                  </DataTableCell>
                  <DataTableCell>{recommendation.reason}</DataTableCell>
                  <DataTableCell>
                    {recommendation.supportingFeatures
                      .slice(0, 3)
                      .map(featureLabel)
                      .join("; ")}
                  </DataTableCell>
                </DataTableRow>
              ))}
            </DataTableBody>
          </DataTable>
        </CardContent>
      </Card>

      <div className="grid gap-6 xl:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Recommendation Rules</CardTitle>
            <CardDescription>Active explainable product rule catalog.</CardDescription>
          </CardHeader>
          <CardContent>
            <DataTable>
              <DataTableHeader>
                <DataTableRow>
                  <DataTableHead>Product</DataTableHead>
                  <DataTableHead>Base Score</DataTableHead>
                  <DataTableHead>Description</DataTableHead>
                </DataTableRow>
              </DataTableHeader>
              <DataTableBody>
                {(rules.data ?? []).map((rule) => (
                  <DataTableRow key={rule.ruleId}>
                    <DataTableCell>{rule.productName}</DataTableCell>
                    <DataTableCell>{formatNumber(rule.baseScore)}</DataTableCell>
                    <DataTableCell>{rule.description}</DataTableCell>
                  </DataTableRow>
                ))}
              </DataTableBody>
            </DataTable>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recommendation History</CardTitle>
            <CardDescription>Latest persisted generation events.</CardDescription>
          </CardHeader>
          <CardContent>
            <DataTable>
              <DataTableHeader>
                <DataTableRow>
                  <DataTableHead>Action</DataTableHead>
                  <DataTableHead>Details</DataTableHead>
                  <DataTableHead>Created</DataTableHead>
                </DataTableRow>
              </DataTableHeader>
              <DataTableBody>
                {(recommendations.data?.history ?? []).map((event) => (
                  <DataTableRow key={event.id}>
                    <DataTableCell>{event.action}</DataTableCell>
                    <DataTableCell>
                      {String(event.details.product_name ?? event.details.reason ?? "")}
                    </DataTableCell>
                    <DataTableCell>
                      {new Date(event.createdAt).toLocaleString()}
                    </DataTableCell>
                  </DataTableRow>
                ))}
              </DataTableBody>
            </DataTable>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
