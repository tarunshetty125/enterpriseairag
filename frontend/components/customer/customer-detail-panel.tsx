"use client";

import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Brain, FileSearch, Sparkles } from "lucide-react";

import { StatusCard } from "@/components/dashboard/status-card";
import { CustomerIntelligenceReportPanel } from "@/components/intelligence/customer-intelligence-report-panel";
import { PageHeader } from "@/components/layout/page-header";
import { formatMs, formatNumber, formatPercent } from "@/components/ml/format";
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
  generateCustomerIntelligenceReport,
  generateRecommendations,
  getCustomer,
  getCustomerBehaviour,
  getCustomerIntelligenceReport,
  getRecommendations,
  getTransactionInsights,
  predictRisk,
  predictSegment,
} from "@/lib/api/platform";

const tabs = [
  "Overview",
  "Features",
  "Risk",
  "Behaviour",
  "Transactions",
  "Recommendations",
  "Policy Evidence",
  "AI Report",
  "Timeline",
] as const;

type Tab = (typeof tabs)[number];

function valueText(value: unknown) {
  if (value === null || value === undefined || value === "") {
    return "Unknown";
  }
  if (typeof value === "number") {
    return formatNumber(value);
  }
  return String(value);
}

function record(value: unknown): Record<string, unknown> {
  return value && typeof value === "object" && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : {};
}

function rows(value: unknown): Array<Record<string, unknown>> {
  return Array.isArray(value)
    ? value.filter((item): item is Record<string, unknown> => Boolean(item))
    : [];
}

export function CustomerDetailPanel({ customerId }: { customerId: string }) {
  const [activeTab, setActiveTab] = useState<Tab>("Overview");
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
  const report = useQuery({
    queryKey: ["customer-intelligence-report", customerId],
    queryFn: () => getCustomerIntelligenceReport(customerId),
    retry: false,
  });
  const risk = useMutation({ mutationFn: predictRisk });
  const segment = useMutation({ mutationFn: predictSegment });
  const recommendationGeneration = useMutation({
    mutationFn: generateRecommendations,
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: ["recommendations", customerId],
      });
    },
  });
  const reportGeneration = useMutation({
    mutationFn: () => generateCustomerIntelligenceReport(customerId, false),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: ["customer-intelligence-report", customerId],
      });
      setActiveTab("AI Report");
    },
  });
  const data = customer.data;
  const policy = record(report.data?.report.policy_validation);
  const citations = rows(policy.citations);
  const timeline = useMemo(
    () => report.data?.workflowTrace ?? [],
    [report.data?.workflowTrace],
  );

  return (
    <div className="space-y-6">
      <PageHeader
        title={data?.fullName ?? customerId}
        description="Premium Customer 360 view with profile, feature store, ML, behaviour, recommendations, policy evidence, and AI report."
      >
        <Badge variant="outline">{customerId}</Badge>
      </PageHeader>

      <div className="grid gap-4 md:grid-cols-4">
        <StatusCard title="Age" value={data?.age ?? "Unknown"} />
        <StatusCard title="Income" value={valueText(data?.estimatedIncome)} />
        <StatusCard title="Credit Score" value={data?.creditScore ?? "Unknown"} />
        <StatusCard title="Products" value={data?.products.length ?? 0} />
      </div>

      <Card>
        <CardContent className="flex flex-wrap gap-2 pt-6">
          {tabs.map((tab) => (
            <Button
              key={tab}
              size="sm"
              variant={activeTab === tab ? "default" : "outline"}
              onClick={() => setActiveTab(tab)}
            >
              {tab}
            </Button>
          ))}
        </CardContent>
      </Card>

      {activeTab === "Overview" ? (
        <div className="grid gap-6 xl:grid-cols-3">
          <Card className="xl:col-span-2">
            <CardHeader>
              <CardTitle>Customer Profile</CardTitle>
              <CardDescription>Canonical financial profile and relationships.</CardDescription>
            </CardHeader>
            <CardContent className="grid gap-3 text-sm md:grid-cols-2">
              {[
                ["Customer ID", data?.customerId],
                ["Gender", data?.gender],
                ["Geography", data?.geography],
                ["Education", data?.education],
                ["Marital Status", data?.maritalStatus],
                ["Income Category", data?.incomeCategory],
                ["Savings Balance", data?.savingsBalance],
                ["Tenure Months", data?.tenureMonths],
              ].map(([label, value]) => (
                <div key={String(label)} className="rounded-md border p-3">
                  <div className="text-xs text-muted-foreground">{label}</div>
                  <div className="mt-1 font-medium">{valueText(value)}</div>
                </div>
              ))}
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Demo Actions</CardTitle>
              <CardDescription>Interview-ready guided actions.</CardDescription>
            </CardHeader>
            <CardContent className="grid gap-2">
              <Button
                disabled={reportGeneration.isPending}
                onClick={() => reportGeneration.mutate()}
              >
                <Sparkles className="h-4 w-4" aria-hidden="true" />
                Generate Customer Report
              </Button>
              <Button
                variant="outline"
                disabled={risk.isPending}
                onClick={() => risk.mutate(customerId)}
              >
                <Brain className="h-4 w-4" aria-hidden="true" />
                Explain Risk
              </Button>
              <Button
                variant="outline"
                disabled={recommendationGeneration.isPending}
                onClick={() => recommendationGeneration.mutate(customerId)}
              >
                <Sparkles className="h-4 w-4" aria-hidden="true" />
                Show Recommendations
              </Button>
              <Button
                variant="outline"
                onClick={() => setActiveTab("Policy Evidence")}
              >
                <FileSearch className="h-4 w-4" aria-hidden="true" />
                Open Policy Evidence
              </Button>
              <Button variant="outline" onClick={() => setActiveTab("Timeline")}>
                View Workflow Trace
              </Button>
            </CardContent>
          </Card>
        </div>
      ) : null}

      {activeTab === "Features" ? (
        <Card>
          <CardHeader>
            <CardTitle>Feature Store Values</CardTitle>
            <CardDescription>Reusable engineered features consumed downstream.</CardDescription>
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
                    <DataTableCell>{valueText(feature.value)}</DataTableCell>
                    <DataTableCell>{feature.description}</DataTableCell>
                    <DataTableCell>{feature.version}</DataTableCell>
                  </DataTableRow>
                ))}
              </DataTableBody>
            </DataTable>
          </CardContent>
        </Card>
      ) : null}

      {activeTab === "Risk" ? (
        <div className="grid gap-6 xl:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Risk Prediction</CardTitle>
              <CardDescription>Random Forest risk model output.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Button disabled={risk.isPending} onClick={() => risk.mutate(customerId)}>
                <Brain className="h-4 w-4" aria-hidden="true" />
                Predict Risk
              </Button>
              <StatusCard
                title="Risk Level"
                value={risk.data?.riskLevel ?? "Run prediction"}
                detail={risk.data ? formatPercent(risk.data.confidence) : undefined}
              />
              <p className="text-sm leading-6 text-muted-foreground">
                {risk.data?.businessExplanation ?? "No prediction has been run yet."}
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Customer Segment</CardTitle>
              <CardDescription>KMeans business label output.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Button
                variant="outline"
                disabled={segment.isPending}
                onClick={() => segment.mutate(customerId)}
              >
                <Brain className="h-4 w-4" aria-hidden="true" />
                Predict Segment
              </Button>
              <StatusCard
                title="Segment"
                value={segment.data?.segmentLabel ?? "Run prediction"}
                detail={segment.data ? formatPercent(segment.data.confidence) : undefined}
              />
            </CardContent>
          </Card>
        </div>
      ) : null}

      {activeTab === "Behaviour" ? (
        <Card>
          <CardHeader>
            <CardTitle>Behaviour Profile</CardTitle>
            <CardDescription>NLP-derived customer behaviour summary.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm leading-6 text-muted-foreground">
              {behaviour.data?.summary ?? "No behaviour profile available."}
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
      ) : null}

      {activeTab === "Transactions" ? (
        <Card>
          <CardHeader>
            <CardTitle>Transaction Intelligence</CardTitle>
            <CardDescription>Classified transactions with keywords and entities.</CardDescription>
          </CardHeader>
          <CardContent>
            <DataTable>
              <DataTableHeader>
                <DataTableRow>
                  <DataTableHead>Category</DataTableHead>
                  <DataTableHead>Amount</DataTableHead>
                  <DataTableHead>Keywords</DataTableHead>
                  <DataTableHead>Sentiment</DataTableHead>
                </DataTableRow>
              </DataTableHeader>
              <DataTableBody>
                {(insights.data?.insights ?? []).slice(0, 50).map((insight) => (
                  <DataTableRow key={insight.id}>
                    <DataTableCell>{insight.category}</DataTableCell>
                    <DataTableCell>{formatNumber(insight.amount)}</DataTableCell>
                    <DataTableCell>{insight.keywords.slice(0, 4).join(", ")}</DataTableCell>
                    <DataTableCell>{insight.sentimentLabel}</DataTableCell>
                  </DataTableRow>
                ))}
              </DataTableBody>
            </DataTable>
          </CardContent>
        </Card>
      ) : null}

      {activeTab === "Recommendations" ? (
        <Card>
          <CardHeader>
            <CardTitle>Recommendations</CardTitle>
            <CardDescription>Explainable product recommendations.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button
              disabled={recommendationGeneration.isPending}
              onClick={() => recommendationGeneration.mutate(customerId)}
            >
              <Sparkles className="h-4 w-4" aria-hidden="true" />
              Generate Recommendations
            </Button>
            <DataTable>
              <DataTableHeader>
                <DataTableRow>
                  <DataTableHead>Product</DataTableHead>
                  <DataTableHead>Score</DataTableHead>
                  <DataTableHead>Confidence</DataTableHead>
                  <DataTableHead>Reason</DataTableHead>
                </DataTableRow>
              </DataTableHeader>
              <DataTableBody>
                {(recommendations.data?.recommendations ?? []).map((item) => (
                  <DataTableRow key={item.id}>
                    <DataTableCell>{item.productName}</DataTableCell>
                    <DataTableCell>{formatNumber(item.suitabilityScore)}</DataTableCell>
                    <DataTableCell>{formatPercent(item.confidence)}</DataTableCell>
                    <DataTableCell>{item.reason}</DataTableCell>
                  </DataTableRow>
                ))}
              </DataTableBody>
            </DataTable>
          </CardContent>
        </Card>
      ) : null}

      {activeTab === "Policy Evidence" ? (
        <Card>
          <CardHeader>
            <CardTitle>Policy Evidence</CardTitle>
            <CardDescription>RAG citations from the generated report.</CardDescription>
          </CardHeader>
          <CardContent>
            <DataTable>
              <DataTableHeader>
                <DataTableRow>
                  <DataTableHead>Document</DataTableHead>
                  <DataTableHead>Section</DataTableHead>
                  <DataTableHead>Chunk</DataTableHead>
                  <DataTableHead>Similarity</DataTableHead>
                </DataTableRow>
              </DataTableHeader>
              <DataTableBody>
                {citations.map((citation) => (
                  <DataTableRow key={`${valueText(citation.document)}-${valueText(citation.chunk)}`}>
                    <DataTableCell>{valueText(citation.document)}</DataTableCell>
                    <DataTableCell>{valueText(citation.section)}</DataTableCell>
                    <DataTableCell>{valueText(citation.chunk)}</DataTableCell>
                    <DataTableCell>
                      {formatNumber(Number(citation.similarity_score ?? 0), 4)}
                    </DataTableCell>
                  </DataTableRow>
                ))}
              </DataTableBody>
            </DataTable>
          </CardContent>
        </Card>
      ) : null}

      {activeTab === "AI Report" ? (
        <CustomerIntelligenceReportPanel customerId={customerId} />
      ) : null}

      {activeTab === "Timeline" ? (
        <Card>
          <CardHeader>
            <CardTitle>Workflow Trace</CardTitle>
            <CardDescription>
              Customer to report execution stages and timings.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <DataTable>
              <DataTableHeader>
                <DataTableRow>
                  <DataTableHead>Stage</DataTableHead>
                  <DataTableHead>Source</DataTableHead>
                  <DataTableHead>Status</DataTableHead>
                  <DataTableHead>Time</DataTableHead>
                  <DataTableHead>Details</DataTableHead>
                </DataTableRow>
              </DataTableHeader>
              <DataTableBody>
                {timeline.map((stage) => (
                  <DataTableRow key={`${stage.stage}-${stage.durationMs}`}>
                    <DataTableCell>{stage.stage}</DataTableCell>
                    <DataTableCell>{stage.source}</DataTableCell>
                    <DataTableCell>{stage.status}</DataTableCell>
                    <DataTableCell>{formatMs(stage.durationMs)}</DataTableCell>
                    <DataTableCell>{stage.details}</DataTableCell>
                  </DataTableRow>
                ))}
              </DataTableBody>
            </DataTable>
          </CardContent>
        </Card>
      ) : null}
    </div>
  );
}
