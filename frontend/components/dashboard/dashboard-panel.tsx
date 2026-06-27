"use client";

import Link from "next/link";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import {
  Brain,
  FileText,
  Gauge,
  Landmark,
  Play,
  ShieldAlert,
  Sparkles,
} from "lucide-react";

import { PageHeader } from "@/components/layout/page-header";
import { StatusCard } from "@/components/dashboard/status-card";
import { formatMs, formatNumber } from "@/components/ml/format";
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
  getCustomers,
  getShowcaseMetrics,
} from "@/lib/api/platform";

function chartRows(rows: Array<Record<string, unknown>>) {
  return rows.map((row) => ({
    label: String(row.label ?? row.provider ?? "Unknown"),
    value: typeof row.value === "number" ? row.value : Number(row.count ?? 0),
  }));
}

const chartColors = [
  "hsl(var(--primary))",
  "hsl(var(--destructive))",
  "hsl(var(--muted-foreground))",
  "hsl(var(--accent-foreground))",
  "hsl(var(--secondary-foreground))",
];

export function DashboardPanel() {
  const queryClient = useQueryClient();
  const metrics = useQuery({
    queryKey: ["platform", "showcase-metrics"],
    queryFn: getShowcaseMetrics,
  });
  const customers = useQuery({
    queryKey: ["customers", 10, 0],
    queryFn: () => getCustomers(10, 0),
  });
  const firstCustomer = customers.data?.items[0]?.customerId;
  const demoGeneration = useMutation({
    mutationFn: (customerId: string) =>
      generateCustomerIntelligenceReport(customerId, false),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: ["platform", "showcase-metrics"],
      });
    },
  });
  const riskData = chartRows(metrics.data?.riskDistribution ?? []);
  const segmentData = chartRows(metrics.data?.segments ?? []);
  const providerUsage = chartRows(metrics.data?.providerUsage ?? []);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Enterprise AI Financial Intelligence"
        description="Executive operating view across data, ML, behaviour intelligence, recommendations, RAG, and the active AI provider."
      >
        <Badge variant="outline">{metrics.data?.health ?? "Checking"}</Badge>
      </PageHeader>

      <Card>
        <CardContent className="grid gap-4 pt-6 md:grid-cols-[1fr_auto] md:items-center">
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
              <Landmark className="h-4 w-4" aria-hidden="true" />
              Interview Demo Mode
            </div>
            <h2 className="text-2xl font-semibold tracking-normal">
              Generate a grounded customer intelligence report from the full AI
              platform pipeline.
            </h2>
            <p className="max-w-3xl text-sm leading-6 text-muted-foreground">
              The demo action runs Customer Profile, Feature Store, Risk Model,
              Segmentation, Behaviour Engine, Recommendation Engine, RAG,
              Context Builder, Prompt, Provider, and Report generation.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <Button
              disabled={!firstCustomer || demoGeneration.isPending}
              onClick={() => firstCustomer && demoGeneration.mutate(firstCustomer)}
            >
              <Play className="h-4 w-4" aria-hidden="true" />
              Generate Customer Report
            </Button>
            {firstCustomer ? (
              <Button asChild variant="outline">
                <Link href={`/customers/${firstCustomer}`}>
                  <FileText className="h-4 w-4" aria-hidden="true" />
                  Open Customer 360
                </Link>
              </Button>
            ) : null}
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatusCard
          title="Customers"
          value={metrics.data?.customers ?? 0}
          detail="Canonical profiles"
        />
        <StatusCard
          title="High Risk"
          value={metrics.data?.highRisk ?? 0}
          detail={`${metrics.data?.mediumRisk ?? 0} medium / ${metrics.data?.lowRisk ?? 0} low`}
        />
        <StatusCard
          title="Recommendations"
          value={metrics.data?.recommendations ?? 0}
          detail="Rules engine outputs"
        />
        <StatusCard
          title="Knowledge Base"
          value={metrics.data?.knowledgeBase ?? 0}
          detail="Indexed policy documents"
        />
        <StatusCard
          title="AI Requests"
          value={metrics.data?.aiRequests ?? 0}
          detail={`${metrics.data?.provider ?? "provider"} / ${metrics.data?.currentModel ?? "model"}`}
        />
        <StatusCard
          title="Recent Reports"
          value={metrics.data?.reportCount ?? 0}
          detail={`${metrics.data?.cacheHits ?? 0} cache hits`}
        />
        <StatusCard
          title="Provider Health"
          value={metrics.data?.health ?? "Unavailable"}
          detail={metrics.data?.provider}
        />
        <StatusCard
          title="Inference Latency"
          value={formatMs(metrics.data?.inferenceLatencyMs ?? 0)}
          detail="Latest AI Gateway event"
        />
      </div>

      <div className="grid gap-6 xl:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <ShieldAlert className="h-4 w-4" aria-hidden="true" />
              Risk Distribution
            </CardTitle>
            <CardDescription>Derived from generated intelligence reports.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[260px]">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie dataKey="value" nameKey="label" data={riskData} outerRadius={92}>
                    {riskData.map((row, index) => (
                      <Cell
                        key={row.label}
                        fill={chartColors[index % chartColors.length]}
                      />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Brain className="h-4 w-4" aria-hidden="true" />
              Customer Segments
            </CardTitle>
            <CardDescription>Business labels from segmentation outputs.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[260px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={segmentData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="label" tickLine={false} axisLine={false} />
                  <YAxis allowDecimals={false} tickLine={false} axisLine={false} />
                  <Tooltip />
                  <Bar dataKey="value" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Gauge className="h-4 w-4" aria-hidden="true" />
              Provider Usage
            </CardTitle>
            <CardDescription>AI Gateway metric events by provider.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[260px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={providerUsage}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="label" tickLine={false} axisLine={false} />
                  <YAxis allowDecimals={false} tickLine={false} axisLine={false} />
                  <Tooltip />
                  <Bar
                    dataKey="value"
                    fill="hsl(var(--secondary-foreground))"
                    radius={[4, 4, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-4 w-4" aria-hidden="true" />
            Recent Intelligence Reports
          </CardTitle>
          <CardDescription>Latest generated reports and cache behaviour.</CardDescription>
        </CardHeader>
        <CardContent>
          <DataTable>
            <DataTableHeader>
              <DataTableRow>
                <DataTableHead>Customer</DataTableHead>
                <DataTableHead>Status</DataTableHead>
                <DataTableHead>Provider</DataTableHead>
                <DataTableHead>Retrieved</DataTableHead>
                <DataTableHead>Cache Hits</DataTableHead>
                <DataTableHead>Generated</DataTableHead>
              </DataTableRow>
            </DataTableHeader>
            <DataTableBody>
              {(metrics.data?.recentReports ?? []).map((report) => (
                <DataTableRow key={report.id}>
                  <DataTableCell>
                    <Link
                      className="font-medium text-primary"
                      href={`/customers/${report.customerId}`}
                    >
                      {report.customerId}
                    </Link>
                  </DataTableCell>
                  <DataTableCell>{report.status}</DataTableCell>
                  <DataTableCell>{report.provider}</DataTableCell>
                  <DataTableCell>{formatNumber(report.retrievedChunks, 0)}</DataTableCell>
                  <DataTableCell>{report.cacheHits}</DataTableCell>
                  <DataTableCell>
                    {new Date(report.generatedAt).toLocaleString()}
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
