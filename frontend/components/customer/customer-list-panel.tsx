"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";

import { PageHeader } from "@/components/layout/page-header";
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
import { getCustomers } from "@/lib/api/platform";

function formatCurrency(value: number | null) {
  if (value === null) {
    return "Unknown";
  }
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value);
}

export function CustomerListPanel() {
  const customers = useQuery({
    queryKey: ["customers", 100, 0],
    queryFn: () => getCustomers(100, 0),
  });

  return (
    <div className="space-y-6">
      <PageHeader
        title="Customers"
        description="Canonical customer records generated from public source datasets."
      />
      <Card>
        <CardHeader>
          <CardTitle>Customer List</CardTitle>
          <CardDescription>
            Showing {customers.data?.items.length ?? 0} of {customers.data?.total ?? 0}
            customers.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <DataTable>
            <DataTableHeader>
              <DataTableRow>
                <DataTableHead>Customer ID</DataTableHead>
                <DataTableHead>Profile</DataTableHead>
                <DataTableHead>Income</DataTableHead>
                <DataTableHead>Credit Score</DataTableHead>
                <DataTableHead>Source</DataTableHead>
              </DataTableRow>
            </DataTableHeader>
            <DataTableBody>
              {(customers.data?.items ?? []).map((customer) => (
                <DataTableRow key={customer.customerId}>
                  <DataTableCell>
                    <Link
                      className="font-medium text-primary hover:underline"
                      href={`/customers/${customer.customerId}`}
                    >
                      {customer.customerId}
                    </Link>
                  </DataTableCell>
                  <DataTableCell>
                    <div className="font-medium">
                      {customer.fullName ?? "Unnamed Customer"}
                    </div>
                    <div className="text-xs text-muted-foreground">
                      {[customer.gender, customer.age, customer.geography]
                        .filter(Boolean)
                        .join(" / ") || "Profile pending"}
                    </div>
                  </DataTableCell>
                  <DataTableCell>
                    <div>{formatCurrency(customer.estimatedIncome)}</div>
                    <div className="text-xs text-muted-foreground">
                      {customer.incomeCategory ?? "Unknown"}
                    </div>
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
