"use client";

import { useEffect, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Tags } from "lucide-react";
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
import { formatNumber } from "@/components/ml/format";
import { Badge } from "@/components/ui/badge";
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
import { getCustomers, getTransactionInsights } from "@/lib/api/platform";

export function TransactionIntelligencePanel() {
  const [customerId, setCustomerId] = useState("");
  const customers = useQuery({
    queryKey: ["customers", 200, 0],
    queryFn: () => getCustomers(200, 0),
  });
  const insights = useQuery({
    queryKey: ["transaction-insights", customerId],
    queryFn: () => getTransactionInsights(customerId),
    enabled: Boolean(customerId),
  });
  const categoryData = useMemo(
    () =>
      Object.entries(insights.data?.categoryDistribution ?? {}).map(
        ([category, count]) => ({
          category,
          count,
          spend: insights.data?.spendingDistribution[category] ?? 0,
        }),
      ),
    [insights.data],
  );
  const totalSpend = useMemo(
    () =>
      Object.values(insights.data?.spendingDistribution ?? {}).reduce(
        (total, amount) => total + amount,
        0,
      ),
    [insights.data?.spendingDistribution],
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
        title="Transaction Intelligence"
        description="Deterministic NLP classification, entity extraction, sentiment, and lifestyle indicators for linked transactions."
      >
        <Badge variant="outline">{customerId || "Select customer"}</Badge>
      </PageHeader>

      <Card>
        <CardHeader>
          <CardTitle>Customer Selector</CardTitle>
          <CardDescription>
            Insights are computed from stored canonical transaction records.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <select
            className="h-9 w-full rounded-md border bg-background px-3 text-sm md:w-[420px]"
            value={customerId}
            onChange={(event) => setCustomerId(event.target.value)}
          >
            {(customers.data?.items ?? []).map((customer) => (
              <option key={customer.customerId} value={customer.customerId}>
                {customer.customerId} / {customer.fullName ?? "Unnamed"}
              </option>
            ))}
          </select>
        </CardContent>
      </Card>

      <div className="grid gap-4 md:grid-cols-3">
        <StatusCard title="Transactions" value={insights.data?.total ?? 0} />
        <StatusCard title="Categories" value={categoryData.length} />
        <StatusCard title="Debit Spend" value={formatNumber(totalSpend)} />
      </div>

      <div className="grid gap-6 xl:grid-cols-3">
        <Card className="xl:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Tags className="h-4 w-4" aria-hidden="true" />
              Category Distribution
            </CardTitle>
            <CardDescription>
              Rule-assisted NLP category counts for the selected customer.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[320px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={categoryData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="category" tickLine={false} axisLine={false} />
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
            <CardTitle>Spending Mix</CardTitle>
            <CardDescription>Debit amount by NLP category.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {categoryData.map((row) => (
              <div key={row.category} className="space-y-1">
                <div className="flex items-center justify-between text-sm">
                  <span>{row.category}</span>
                  <span className="text-muted-foreground">
                    {formatNumber(row.spend)}
                  </span>
                </div>
                <div className="h-2 overflow-hidden rounded-full bg-muted">
                  <div
                    className="h-full rounded-full bg-primary"
                    style={{
                      width: `${totalSpend ? (row.spend / totalSpend) * 100 : 0}%`,
                    }}
                  />
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Transaction Insights</CardTitle>
          <CardDescription>
            Stored NLP outputs with keywords, entities, sentiment, and indicators.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <DataTable>
            <DataTableHeader>
              <DataTableRow>
                <DataTableHead>Description</DataTableHead>
                <DataTableHead>Category</DataTableHead>
                <DataTableHead>Amount</DataTableHead>
                <DataTableHead>Sentiment</DataTableHead>
                <DataTableHead>Indicators</DataTableHead>
              </DataTableRow>
            </DataTableHeader>
            <DataTableBody>
              {(insights.data?.insights ?? []).slice(0, 50).map((insight) => (
                <DataTableRow key={insight.id}>
                  <DataTableCell>{insight.rawDescription}</DataTableCell>
                  <DataTableCell>{insight.category}</DataTableCell>
                  <DataTableCell>{formatNumber(insight.amount)}</DataTableCell>
                  <DataTableCell>{insight.sentimentLabel}</DataTableCell>
                  <DataTableCell>
                    {insight.lifestyleIndicators.slice(0, 3).join(", ") || "None"}
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
