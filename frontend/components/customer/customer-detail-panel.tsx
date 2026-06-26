"use client";

import { useQuery } from "@tanstack/react-query";

import { StatusCard } from "@/components/dashboard/status-card";
import { PageHeader } from "@/components/layout/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  DataTable,
  DataTableBody,
  DataTableCell,
  DataTableHead,
  DataTableHeader,
  DataTableRow,
} from "@/components/ui/data-table";
import { getCustomer } from "@/lib/api/platform";

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
  const customer = useQuery({
    queryKey: ["customers", customerId],
    queryFn: () => getCustomer(customerId),
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
            <CardTitle>Transactions</CardTitle>
          </CardHeader>
          <CardContent>
            <DataTable>
              <DataTableBody>
                {(data?.transactions ?? []).slice(0, 10).map((transaction) => (
                  <DataTableRow key={transaction.id}>
                    <DataTableCell>{transaction.category}</DataTableCell>
                    <DataTableCell>{formatValue(transaction.amount)}</DataTableCell>
                    <DataTableCell>{transaction.direction}</DataTableCell>
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
