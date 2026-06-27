"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Brain, Sparkles } from "lucide-react";

import { StatusCard } from "@/components/dashboard/status-card";
import { PageHeader } from "@/components/layout/page-header";
import { formatPercent } from "@/components/ml/format";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
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
  getCustomer,
  getCustomerBehaviour,
  getRecommendations,
  getTransactionInsights,
  predictRisk,
  predictSegment,
} from "@/lib/api/platform";

function formatValue(value: unknown) {
  if (value === null || value === undefined) {
    return "Unknown";
  }
  if (typeof value === "number") {
    return value.toLocaleString();
  }
  return String(value);
}

export function CustomerDetailPanel({ customerId }: { customerId: string }) {
  const queryClient = useQueryClient();
  const customer = useQuery({
    queryKey: ["customers", customerId],
    queryFn: () => getCustomer(customerId),
  });
  const behaviour = useQuery({
    queryKey: ["customer-behaviour", customerId],
    queryFn: () => getCustomerBehaviour(customerId),
  });
  const insights = useQuery({
    queryKey: ["transaction-insights", customerId],
    queryFn: () => getTransactionInsights(customerId),
  });
  const recommendations = useQuery({
    queryKey: ["recommendations", customerId],
    queryFn: () => getRecommendations(customerId),
  });
  const risk = useMutation({
    mutationFn: predictRisk,
  });
  const segment = useMutation({
    mutationFn: predictSegment,
  });
  const recommendationGeneration = useMutation({
    mutationFn: generateRecommendations,
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: ["recommendations", customerId],
      });
    },
  });
  const data = customer.data;

  return (
    <div className="space-y-6">
      <PageHeader
        title={data?.fullName ?? customerId}
        description="Customer profile, linked products, transactions, loans, and feature store values."
      />
      <div className="grid gap-4 md:grid-cols-4">
        <StatusCard title="Age" value={data?.age ?? "Unknown"} />
        <StatusCard title="Income" value={formatValue(data?.estimatedIncome)} />
        <StatusCard title="Products" value={data?.products.length ?? 0} />
        <StatusCard title="Feature Count" value={data?.features.length ?? 0} />
      </div>
      <div className="grid gap-6 xl:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>ML Predictions</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex flex-wrap gap-2">
              <Button
                size="sm"
                disabled={risk.isPending}
                onClick={() => risk.mutate(customerId)}
              >
                <Brain className="h-4 w-4" aria-hidden="true" />
                Risk
              </Button>
              <Button
                size="sm"
                variant="outline"
                disabled={segment.isPending}
                onClick={() => segment.mutate(customerId)}
              >
                <Brain className="h-4 w-4" aria-hidden="true" />
                Segment
              </Button>
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Risk Level</span>
                <span>{risk.data?.riskLevel ?? "Run prediction"}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Risk Confidence</span>
                <span>
                  {risk.data ? formatPercent(risk.data.confidence) : "Unavailable"}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Segment</span>
                <span>{segment.data?.segmentLabel ?? "Run prediction"}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Behaviour Profile</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <p className="text-sm leading-6 text-muted-foreground">
              {behaviour.data?.summary ?? "No behaviour profile available yet."}
            </p>
            <div className="flex flex-wrap gap-2">
              {(behaviour.data?.flags ?? []).map((flag) => (
                <Badge key={flag} variant="secondary">
                  {flag}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recommendations</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button
              size="sm"
              disabled={recommendationGeneration.isPending}
              onClick={() => recommendationGeneration.mutate(customerId)}
            >
              <Sparkles className="h-4 w-4" aria-hidden="true" />
              Generate
            </Button>
            {(recommendations.data?.recommendations ?? []).slice(0, 3).map((item) => (
              <div key={item.id} className="rounded-md border p-3 text-sm">
                <div className="flex items-center justify-between gap-3">
                  <span className="font-medium">{item.productName}</span>
                  <Badge variant="outline">{formatValue(item.suitabilityScore)}</Badge>
                </div>
                <p className="mt-2 text-xs text-muted-foreground">{item.reason}</p>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Customer Profile</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-3 text-sm md:grid-cols-2">
          {data
            ? [
                ["Customer ID", data.customerId],
                ["Gender", data.gender],
                ["Geography", data.geography],
                ["Education", data.education],
                ["Marital Status", data.maritalStatus],
                ["Income Category", data.incomeCategory],
                ["Credit Score", data.creditScore],
                ["Tenure Months", data.tenureMonths],
                ["Savings Balance", data.savingsBalance],
                ["Source Dataset", data.sourceDataset],
              ].map(([label, value]) => (
                <div key={String(label)} className="rounded-md border p-3">
                  <div className="text-xs text-muted-foreground">{label}</div>
                  <div className="mt-1 font-medium">{formatValue(value)}</div>
                </div>
              ))
            : null}
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>Feature Store Values</CardTitle>
        </CardHeader>
        <CardContent>
          <DataTable>
            <DataTableHeader>
              <DataTableRow>
                <DataTableHead>Feature</DataTableHead>
                <DataTableHead>Value</DataTableHead>
                <DataTableHead>Description</DataTableHead>
                <DataTableHead>Version</DataTableHead>
              </DataTableRow>
            </DataTableHeader>
            <DataTableBody>
              {(data?.features ?? []).map((feature) => (
                <DataTableRow key={feature.name}>
                  <DataTableCell>{feature.name}</DataTableCell>
                  <DataTableCell>{formatValue(feature.value)}</DataTableCell>
                  <DataTableCell>{feature.description}</DataTableCell>
                  <DataTableCell>{feature.version}</DataTableCell>
                </DataTableRow>
              ))}
            </DataTableBody>
          </DataTable>
        </CardContent>
      </Card>
      <div className="grid gap-6 xl:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Loans</CardTitle>
          </CardHeader>
          <CardContent>
            <DataTable>
              <DataTableBody>
                {(data?.loans ?? []).map((loan) => (
                  <DataTableRow key={loan.id}>
                    <DataTableCell>{loan.loanType}</DataTableCell>
                    <DataTableCell>{formatValue(loan.amount)}</DataTableCell>
                    <DataTableCell>{loan.status}</DataTableCell>
                  </DataTableRow>
                ))}
              </DataTableBody>
            </DataTable>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Products</CardTitle>
          </CardHeader>
          <CardContent>
            <DataTable>
              <DataTableBody>
                {(data?.products ?? []).map((product) => (
                  <DataTableRow key={product.id}>
                    <DataTableCell>{product.productType}</DataTableCell>
                    <DataTableCell>{product.status}</DataTableCell>
                    <DataTableCell>{formatValue(product.revenue)}</DataTableCell>
                  </DataTableRow>
                ))}
              </DataTableBody>
            </DataTable>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Transaction Intelligence</CardTitle>
          </CardHeader>
          <CardContent>
            <DataTable>
              <DataTableHeader>
                <DataTableRow>
                  <DataTableHead>Category</DataTableHead>
                  <DataTableHead>Amount</DataTableHead>
                  <DataTableHead>Sentiment</DataTableHead>
                </DataTableRow>
              </DataTableHeader>
              <DataTableBody>
                {(insights.data?.insights ?? []).slice(0, 10).map((insight) => (
                  <DataTableRow key={insight.id}>
                    <DataTableCell>{insight.category}</DataTableCell>
                    <DataTableCell>{formatValue(insight.amount)}</DataTableCell>
                    <DataTableCell>{insight.sentimentLabel}</DataTableCell>
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
