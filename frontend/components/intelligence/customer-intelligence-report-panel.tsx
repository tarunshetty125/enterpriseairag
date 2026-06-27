"use client";

import { useMemo } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Copy,
  Download,
  FileJson,
  FileText,
  Printer,
  RefreshCw,
  ShieldCheck,
  Workflow,
} from "lucide-react";

import { StatusCard } from "@/components/dashboard/status-card";
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
  exportCustomerIntelligenceReport,
  generateCustomerIntelligenceReport,
  getCustomerIntelligenceReport,
} from "@/lib/api/platform";
import type { CustomerIntelligenceReport } from "@/types/platform";

function record(value: unknown): Record<string, unknown> {
  return value && typeof value === "object" && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : {};
}

function list(value: unknown): Array<Record<string, unknown>> {
  return Array.isArray(value)
    ? value.filter((item): item is Record<string, unknown> => Boolean(item))
    : [];
}

function text(value: unknown, fallback = "Unavailable") {
  if (value === null || value === undefined || value === "") {
    return fallback;
  }
  return String(value);
}

function numberValue(value: unknown) {
  return typeof value === "number" ? value : 0;
}

function reportMarkdown(report: CustomerIntelligenceReport) {
  const payload = report.report;
  const executive = record(payload.executive_summary);
  const risk = record(payload.risk_assessment);
  const behaviour = record(payload.behaviour_analysis);
  const aiSummary = record(payload.ai_summary);
  return [
    "# Customer Intelligence Report",
    "",
    `Customer: ${report.customerId}`,
    `Status: ${report.status}`,
    `Provider: ${report.provider}`,
    `Model: ${report.model}`,
    "",
    "## Executive Summary",
    text(executive.overall_assessment),
    "",
    "## Risk Assessment",
    `${text(risk.current_risk)} / ${text(risk.confidence)}`,
    text(risk.business_explanation),
    "",
    "## Behaviour Analysis",
    text(behaviour.summary),
    "",
    "## AI Summary",
    text(aiSummary.narrative),
  ].join("\n");
}

async function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}

export function CustomerIntelligenceReportPanel({
  customerId,
}: {
  customerId: string;
}) {
  const queryClient = useQueryClient();
  const report = useQuery({
    queryKey: ["customer-intelligence-report", customerId],
    queryFn: () => getCustomerIntelligenceReport(customerId),
    retry: false,
  });
  const generation = useMutation({
    mutationFn: (force: boolean) =>
      generateCustomerIntelligenceReport(customerId, force),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: ["customer-intelligence-report", customerId],
      });
      await queryClient.invalidateQueries({
        queryKey: ["platform", "showcase-metrics"],
      });
    },
  });
  const data = generation.data ?? report.data;
  const payload = data?.report ?? {};
  const executive = record(payload.executive_summary);
  const risk = record(payload.risk_assessment);
  const behaviour = record(payload.behaviour_analysis);
  const policy = record(payload.policy_validation);
  const aiSummary = record(payload.ai_summary);
  const recommendations = list(payload.product_recommendations);
  const citations = list(policy.citations);
  const chunks = list(record(payload.explainability).retrieved_chunks);
  const trace = useMemo(() => data?.workflowTrace ?? [], [data?.workflowTrace]);
  const totalWorkflowMs = useMemo(
    () => trace.reduce((total, stage) => total + stage.durationMs, 0),
    [trace],
  );

  const handleExport = async (format: "pdf" | "markdown" | "json") => {
    const blob = await exportCustomerIntelligenceReport(customerId, format);
    await downloadBlob(blob, `${customerId}-intelligence-report.${format === "markdown" ? "md" : format}`);
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader className="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
          <div className="space-y-2">
            <CardTitle>AI Customer Intelligence Report</CardTitle>
            <CardDescription>
              Flagship report composed from the feature store, ML models,
              transaction intelligence, recommendations, policy retrieval, and
              the active AI provider.
            </CardDescription>
            <div className="flex flex-wrap gap-2">
              <Badge variant="outline">{data?.status ?? "No report"}</Badge>
              <Badge variant="secondary">
                {data?.cacheHit ? "Cache hit" : "Fresh or pending"}
              </Badge>
              <Badge variant="outline">{data?.promptVersion ?? "No prompt"}</Badge>
            </div>
          </div>
          <div className="flex flex-wrap gap-2">
            <Button
              size="sm"
              disabled={generation.isPending}
              onClick={() => generation.mutate(false)}
            >
              <RefreshCw className="h-4 w-4" aria-hidden="true" />
              Generate
            </Button>
            <Button
              size="sm"
              variant="outline"
              disabled={generation.isPending}
              onClick={() => generation.mutate(true)}
            >
              <RefreshCw className="h-4 w-4" aria-hidden="true" />
              Regenerate
            </Button>
            <Button
              size="sm"
              variant="outline"
              disabled={!data}
              onClick={() => data && navigator.clipboard.writeText(reportMarkdown(data))}
            >
              <Copy className="h-4 w-4" aria-hidden="true" />
              Copy
            </Button>
            <Button size="sm" variant="outline" onClick={() => window.print()}>
              <Printer className="h-4 w-4" aria-hidden="true" />
              Print
            </Button>
          </div>
        </CardHeader>
        <CardContent className="grid gap-4 md:grid-cols-4">
          <StatusCard
            title="Risk"
            value={text(risk.current_risk)}
            detail={formatPercent(numberValue(risk.confidence))}
          />
          <StatusCard
            title="Retrieved Chunks"
            value={data?.retrievedChunks ?? 0}
            detail={`${citations.length} citations`}
          />
          <StatusCard
            title="Provider"
            value={data?.provider ?? "Unavailable"}
            detail={data?.model}
          />
          <StatusCard
            title="Workflow Time"
            value={formatMs(totalWorkflowMs)}
            detail={`${data?.cacheHits ?? 0} cache hits`}
          />
        </CardContent>
      </Card>

      <div className="grid gap-6 xl:grid-cols-3">
        <Card className="xl:col-span-2">
          <CardHeader>
            <CardTitle>Executive Summary</CardTitle>
            <CardDescription>Grounded assessment for relationship managers.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4 text-sm leading-6 text-muted-foreground">
            <p>{text(executive.overall_assessment, "Generate a report to view summary.")}</p>
            <div className="rounded-md border p-4">
              <div className="mb-2 flex items-center gap-2 font-medium text-foreground">
                <ShieldCheck className="h-4 w-4" aria-hidden="true" />
                AI Summary
              </div>
              <p>{text(aiSummary.narrative, "No AI narrative available yet.")}</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Exports</CardTitle>
            <CardDescription>Exported reports preserve citations.</CardDescription>
          </CardHeader>
          <CardContent className="grid gap-2">
            <Button
              variant="outline"
              disabled={!data}
              onClick={() => handleExport("pdf")}
            >
              <Download className="h-4 w-4" aria-hidden="true" />
              PDF
            </Button>
            <Button
              variant="outline"
              disabled={!data}
              onClick={() => handleExport("markdown")}
            >
              <FileText className="h-4 w-4" aria-hidden="true" />
              Markdown
            </Button>
            <Button
              variant="outline"
              disabled={!data}
              onClick={() => handleExport("json")}
            >
              <FileJson className="h-4 w-4" aria-hidden="true" />
              JSON
            </Button>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Risk Assessment</CardTitle>
            <CardDescription>Feature importance and model explanation.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <p className="text-sm text-muted-foreground">
              {text(risk.business_explanation)}
            </p>
            {list(risk.key_drivers).map((feature) => (
              <div
                key={text(feature.name)}
                className="flex items-center justify-between rounded-md border p-3 text-sm"
              >
                <span>{text(feature.name)}</span>
                <Badge variant="outline">
                  {formatNumber(numberValue(feature.importance), 4)}
                </Badge>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Behaviour Analysis</CardTitle>
            <CardDescription>Deterministic NLP and behaviour features.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <p className="text-sm leading-6 text-muted-foreground">
              {text(behaviour.summary)}
            </p>
            <div className="flex flex-wrap gap-2">
              {Array.isArray(behaviour.transaction_behaviour)
                ? behaviour.transaction_behaviour.map((flag) => (
                    <Badge key={String(flag)} variant="secondary">
                      {String(flag)}
                    </Badge>
                  ))
                : null}
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Product Recommendations</CardTitle>
          <CardDescription>Explainable recommendations from the rules engine.</CardDescription>
        </CardHeader>
        <CardContent>
          <DataTable>
            <DataTableHeader>
              <DataTableRow>
                <DataTableHead>Product</DataTableHead>
                <DataTableHead>Suitability</DataTableHead>
                <DataTableHead>Confidence</DataTableHead>
                <DataTableHead>Reason</DataTableHead>
              </DataTableRow>
            </DataTableHeader>
            <DataTableBody>
              {recommendations.map((item) => (
                <DataTableRow key={`${text(item.product_name)}-${text(item.reason)}`}>
                  <DataTableCell>{text(item.product_name)}</DataTableCell>
                  <DataTableCell>
                    {formatNumber(numberValue(item.suitability_score))}
                  </DataTableCell>
                  <DataTableCell>
                    {formatPercent(numberValue(item.confidence))}
                  </DataTableCell>
                  <DataTableCell>{text(item.reason)}</DataTableCell>
                </DataTableRow>
              ))}
            </DataTableBody>
          </DataTable>
        </CardContent>
      </Card>

      <div className="grid gap-6 xl:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Policy Evidence</CardTitle>
            <CardDescription>Retrieved RAG citations supporting validation.</CardDescription>
          </CardHeader>
          <CardContent>
            <DataTable>
              <DataTableHeader>
                <DataTableRow>
                  <DataTableHead>Document</DataTableHead>
                  <DataTableHead>Section</DataTableHead>
                  <DataTableHead>Score</DataTableHead>
                </DataTableRow>
              </DataTableHeader>
              <DataTableBody>
                {citations.map((citation) => (
                  <DataTableRow key={`${text(citation.document)}-${text(citation.chunk)}`}>
                    <DataTableCell>{text(citation.document)}</DataTableCell>
                    <DataTableCell>{text(citation.section)}</DataTableCell>
                    <DataTableCell>
                      {formatNumber(numberValue(citation.similarity_score), 4)}
                    </DataTableCell>
                  </DataTableRow>
                ))}
              </DataTableBody>
            </DataTable>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Workflow className="h-4 w-4" aria-hidden="true" />
              Workflow Trace
            </CardTitle>
            <CardDescription>End-to-end execution path and timings.</CardDescription>
          </CardHeader>
          <CardContent>
            <DataTable>
              <DataTableHeader>
                <DataTableRow>
                  <DataTableHead>Stage</DataTableHead>
                  <DataTableHead>Status</DataTableHead>
                  <DataTableHead>Time</DataTableHead>
                </DataTableRow>
              </DataTableHeader>
              <DataTableBody>
                {trace.map((stage) => (
                  <DataTableRow key={`${stage.stage}-${stage.durationMs}`}>
                    <DataTableCell>{stage.stage}</DataTableCell>
                    <DataTableCell>{stage.status}</DataTableCell>
                    <DataTableCell>{formatMs(stage.durationMs)}</DataTableCell>
                  </DataTableRow>
                ))}
              </DataTableBody>
            </DataTable>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Highlighted Evidence</CardTitle>
          <CardDescription>Retrieved chunks used by the report.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {chunks.slice(0, 4).map((chunk) => (
            <div key={text(chunk.chunk)} className="rounded-md border p-4 text-sm">
              <div className="mb-2 flex flex-wrap items-center gap-2">
                <Badge variant="outline">{text(chunk.document)}</Badge>
                <Badge variant="secondary">{text(chunk.section)}</Badge>
                <span className="text-xs text-muted-foreground">
                  Similarity {formatNumber(numberValue(chunk.similarity_score), 4)}
                </span>
              </div>
              <p className="leading-6 text-muted-foreground">{text(chunk.content)}</p>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
