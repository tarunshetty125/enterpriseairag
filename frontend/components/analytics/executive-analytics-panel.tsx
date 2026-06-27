"use client";

import { useQuery } from "@tanstack/react-query";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  Cell,
} from "recharts";

import { StatusCard } from "@/components/dashboard/status-card";
import { PageHeader } from "@/components/layout/page-header";
import { formatMs } from "@/components/ml/format";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { getIntelligenceStatus, getShowcaseMetrics } from "@/lib/api/platform";

const colors = [
  "hsl(var(--primary))",
  "hsl(var(--destructive))",
  "hsl(var(--muted-foreground))",
  "hsl(var(--secondary-foreground))",
];

function chartRows(rows: Array<Record<string, unknown>>) {
  return rows.map((row) => ({
    label: String(row.label ?? row.provider ?? "Unknown"),
    value: typeof row.value === "number" ? row.value : Number(row.count ?? 0),
  }));
}

export function ExecutiveAnalyticsPanel() {
  const metrics = useQuery({
    queryKey: ["platform", "showcase-metrics"],
    queryFn: getShowcaseMetrics,
  });
  const intelligence = useQuery({
    queryKey: ["platform", "intelligence-status"],
    queryFn: getIntelligenceStatus,
  });
  const riskData = chartRows(metrics.data?.riskDistribution ?? []);
  const segmentData = chartRows(metrics.data?.segments ?? []);
  const providerData = chartRows(metrics.data?.providerUsage ?? []);
  const reportTrend = (metrics.data?.recentReports ?? [])
    .slice()
    .reverse()
    .map((report, index) => ({
      index: index + 1,
      latency: report.latencyMs,
      context: report.contextSize,
      retrieved: report.retrievedChunks,
    }));

  return (
    <div className="space-y-6">
      <PageHeader
        title="Executive Analytics"
        description="Showcase analytics for risk, segments, recommendations, behaviour intelligence, knowledge usage, provider usage, and inference latency."
      />

      <div className="grid gap-4 md:grid-cols-4">
        <StatusCard
          title="Reports"
          value={metrics.data?.reportCount ?? 0}
          detail={`${metrics.data?.cacheHits ?? 0} cache hits`}
        />
        <StatusCard
          title="Recommendations"
          value={metrics.data?.recommendations ?? 0}
          detail="Generated product actions"
        />
        <StatusCard
          title="Behaviour Profiles"
          value={intelligence.data?.behaviourProfilesGenerated ?? 0}
          detail={`${intelligence.data?.transactionsProcessed ?? 0} transactions`}
        />
        <StatusCard
          title="Provider Latency"
          value={formatMs(metrics.data?.inferenceLatencyMs ?? 0)}
          detail={metrics.data?.currentModel}
        />
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Risk Distribution</CardTitle>
            <CardDescription>High, medium, and low risk report outcomes.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[320px]">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={riskData} dataKey="value" nameKey="label" outerRadius={110}>
                    {riskData.map((row, index) => (
                      <Cell key={row.label} fill={colors[index % colors.length]} />
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
            <CardTitle>Customer Segments</CardTitle>
            <CardDescription>Business labels emitted by segmentation.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[320px]">
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
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Provider Usage</CardTitle>
            <CardDescription>AI Gateway calls grouped by provider.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={providerData}>
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

        <Card>
          <CardHeader>
            <CardTitle>Inference Latency</CardTitle>
            <CardDescription>Recent report latency and retrieval volume.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={reportTrend}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="index" tickLine={false} axisLine={false} />
                  <YAxis tickLine={false} axisLine={false} />
                  <Tooltip />
                  <Line
                    type="monotone"
                    dataKey="latency"
                    stroke="hsl(var(--primary))"
                    strokeWidth={2}
                  />
                  <Line
                    type="monotone"
                    dataKey="retrieved"
                    stroke="hsl(var(--destructive))"
                    strokeWidth={2}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
