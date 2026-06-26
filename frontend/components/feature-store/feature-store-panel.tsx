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
import { getCustomers, getFeatureStoreStatus } from "@/lib/api/platform";

export function FeatureStorePanel() {
  const status = useQuery({
    queryKey: ["feature-store", "status"],
    queryFn: getFeatureStoreStatus,
  });
  const customers = useQuery({
    queryKey: ["customers", 25, 0],
    queryFn: () => getCustomers(25, 0),
  });

  return (
    <div className="space-y-6">
      <PageHeader
        title="Feature Store"
        description="Versioned reusable customer features generated from canonical data."
      />
      <div className="grid gap-4 md:grid-cols-4">
        <StatusCard title="Version" value={status.data?.featureVersion ?? "None"} />
        <StatusCard
          title="Snapshots"
          value={status.data?.snapshotCount ?? 0}
          detail={`${status.data?.customerCount ?? 0} customers`}
        />
        <StatusCard
          title="Coverage"
          value={`${Math.round((status.data?.coverage ?? 0) * 100)}%`}
        />
        <StatusCard title="Feature Count" value={status.data?.featureCount ?? 0} />
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Customers With Feature Snapshots</CardTitle>
        </CardHeader>
        <CardContent>
          <DataTable>
            <DataTableHeader>
              <DataTableRow>
                <DataTableHead>Customer</DataTableHead>
                <DataTableHead>Income</DataTableHead>
                <DataTableHead>Credit Score</DataTableHead>
                <DataTableHead>Source</DataTableHead>
              </DataTableRow>
            </DataTableHeader>
            <DataTableBody>
              {(customers.data?.items ?? []).map((customer) => (
                <DataTableRow key={customer.customerId}>
                  <DataTableCell>{customer.customerId}</DataTableCell>
                  <DataTableCell>
                    {customer.estimatedIncome?.toLocaleString() ?? "Unknown"}
                  </DataTableCell>
                  <DataTableCell>{customer.creditScore ?? "Unknown"}</DataTableCell>
                  <DataTableCell>{customer.sourceDataset}</DataTableCell>
                </DataTableRow>
              ))}
            </DataTableBody>
          </DataTable>
        </CardContent>
      </Card>
    </div>
  );
}
