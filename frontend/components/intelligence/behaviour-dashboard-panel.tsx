"use client";

import { useEffect, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Activity, BadgeCheck } from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
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
import { getCustomerBehaviour, getCustomers } from "@/lib/api/platform";

function asNumber(value: unknown) {
  return typeof value === "number" ? value : 0;
}

export function BehaviourDashboardPanel() {
  const [customerId, setCustomerId] = useState("");
  const customers = useQuery({
    queryKey: ["customers", 200, 0],
    queryFn: () => getCustomers(200, 0),
  });
  const behaviour = useQuery({
    queryKey: ["customer-behaviour", customerId],
    queryFn: () => getCustomerBehaviour(customerId),
    enabled: Boolean(customerId),
  });
  const categorySpend = useMemo(
    () =>
      Object.entries(behaviour.data?.categorySpend ?? {}).map(
        ([category, amount]) => ({
          category,
          amount,
        }),
      ),
    [behaviour.data?.categorySpend],
  );
  const monthlyTrends = useMemo(
    () =>
      (behaviour.data?.monthlyTrends ?? []).map((row) => ({
        period: String(row.period ?? "Period"),
        credit: asNumber(row.credit),
        debit: asNumber(row.debit),
        count: asNumber(row.count),
      })),
    [behaviour.data?.monthlyTrends],
  );
  const topMerchants = useMemo(
    () =>
      (behaviour.data?.topMerchants ?? []).map((row) => ({
        name: String(row.name ?? "Unknown"),
        amount: asNumber(row.amount),
        count: asNumber(row.count),
      })),
    [behaviour.data?.topMerchants],
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
        title="Behaviour Dashboard"
        description="Customer-level behavioural profile generated from deterministic transaction intelligence."
      >
        <Badge variant="outline">{behaviour.data?.profileVersion ?? "No profile"}</Badge>
      </PageHeader>

      <Card>
        <CardHeader>
          <CardTitle>Customer Behaviour Profile</CardTitle>
          <CardDescription>
            Select a customer to compute or refresh the stored behaviour profile.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
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
          {behaviour.data ? (
            <p className="text-sm leading-6 text-muted-foreground">
              {behaviour.data.summary}
            </p>
          ) : null}
        </CardContent>
      </Card>

      <div className="grid gap-4 md:grid-cols-4">
        <StatusCard
          title="Behaviour Flags"
          value={behaviour.data?.flags.length ?? 0}
        />
        <StatusCard
          title="Lifestyle Signals"
          value={behaviour.data?.lifestyleIndicators.length ?? 0}
        />
        <StatusCard
          title="Transactions"
          value={asNumber(behaviour.data?.features["transaction_count"])}
        />
        <StatusCard
          title="NLP Time"
          value={`${formatNumber(behaviour.data?.processingTimeMs ?? 0)} ms`}
        />
      </div>

      <div className="grid gap-6 xl:grid-cols-3">
        <Card className="xl:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-4 w-4" aria-hidden="true" />
              Monthly Trends
            </CardTitle>
            <CardDescription>Credit and debit totals by synthetic period.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[320px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={monthlyTrends}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="period" tickLine={false} axisLine={false} />
                  <YAxis tickLine={false} axisLine={false} />
                  <Tooltip />
                  <Line
                    type="monotone"
                    dataKey="credit"
                    stroke="hsl(var(--primary))"
                    strokeWidth={2}
                  />
                  <Line
                    type="monotone"
                    dataKey="debit"
                    stroke="hsl(var(--destructive))"
                    strokeWidth={2}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BadgeCheck className="h-4 w-4" aria-hidden="true" />
              Behaviour Flags
            </CardTitle>
            <CardDescription>Rule-derived customer behaviour markers.</CardDescription>
          </CardHeader>
          <CardContent className="flex flex-wrap gap-2">
            {(behaviour.data?.flags ?? []).map((flag) => (
              <Badge key={flag} variant="secondary">
                {flag}
              </Badge>
            ))}
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Spending Distribution</CardTitle>
            <CardDescription>Debit spend grouped by NLP category.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[280px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={categorySpend}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="category" tickLine={false} axisLine={false} />
                  <YAxis tickLine={false} axisLine={false} />
                  <Tooltip />
                  <Bar
                    dataKey="amount"
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
            <CardTitle>Top Merchants</CardTitle>
            <CardDescription>Largest counterparties from extracted entities.</CardDescription>
          </CardHeader>
          <CardContent>
            <DataTable>
              <DataTableHeader>
                <DataTableRow>
                  <DataTableHead>Merchant</DataTableHead>
                  <DataTableHead>Amount</DataTableHead>
                  <DataTableHead>Count</DataTableHead>
                </DataTableRow>
              </DataTableHeader>
              <DataTableBody>
                {topMerchants.map((merchant) => (
                  <DataTableRow key={merchant.name}>
                    <DataTableCell>{merchant.name}</DataTableCell>
                    <DataTableCell>{formatNumber(merchant.amount)}</DataTableCell>
                    <DataTableCell>{merchant.count}</DataTableCell>
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
