"use client";

import { useEffect, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { AlertTriangle, Gauge } from "lucide-react";

import { PageHeader } from "@/components/layout/page-header";
import { formatNumber, formatPercent } from "@/components/ml/format";
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
import { getCustomers, getMLModels, predictRisk } from "@/lib/api/platform";

export function RiskPredictionPanel() {
  const [customerId, setCustomerId] = useState("");
  const customers = useQuery({
    queryKey: ["customers", 100, 0],
    queryFn: () => getCustomers(100, 0),
  });
  const models = useQuery({
    queryKey: ["ml", "models"],
    queryFn: getMLModels,
  });
  const activeRisk = models.data?.models.find(
    (model) => model.modelName === "risk_prediction" && model.activeModel,
  );
  const prediction = useMutation({
    mutationFn: predictRisk,
  });

  useEffect(() => {
    const firstCustomer = customers.data?.items[0]?.customerId;
    if (!customerId && firstCustomer) {
      setCustomerId(firstCustomer);
    }
  }, [customerId, customers.data?.items]);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Risk Prediction"
        description="Run the active Random Forest risk model against a real customer feature snapshot."
      >
        <Badge variant="outline">
          {activeRisk ? `Active ${activeRisk.version}` : "No active model"}
        </Badge>
      </PageHeader>

      <Card>
        <CardHeader>
          <CardTitle>Customer Input</CardTitle>
          <CardDescription>
            Predictions are generated from Phase 2 feature snapshots.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-3 md:flex-row">
          <select
            className="h-9 rounded-md border bg-background px-3 text-sm"
            value={customerId}
            onChange={(event) => setCustomerId(event.target.value)}
          >
            {(customers.data?.items ?? []).map((customer) => (
              <option key={customer.customerId} value={customer.customerId}>
                {customer.customerId} / {customer.fullName ?? "Unnamed"}
              </option>
            ))}
          </select>
          <Button
            disabled={!customerId || prediction.isPending}
            onClick={() => prediction.mutate(customerId)}
          >
            <Gauge className="h-4 w-4" aria-hidden="true" />
            Predict Risk
          </Button>
        </CardContent>
      </Card>

      {prediction.error ? (
        <Card className="border-destructive/40">
          <CardContent className="flex items-center gap-2 pt-6 text-sm text-destructive">
            <AlertTriangle className="h-4 w-4" aria-hidden="true" />
            {prediction.error.message}
          </CardContent>
        </Card>
      ) : null}

      {prediction.data ? (
        <div className="grid gap-4 xl:grid-cols-3">
          <Card>
            <CardHeader>
              <CardTitle>Prediction</CardTitle>
              <CardDescription>{prediction.data.modelVersion}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <div className="text-sm text-muted-foreground">Risk Level</div>
                <div className="text-3xl font-semibold tracking-normal">
                  {prediction.data.riskLevel}
                </div>
              </div>
              <div>
                <div className="text-sm text-muted-foreground">Confidence</div>
                <div className="text-xl font-semibold tracking-normal">
                  {formatPercent(prediction.data.confidence)}
                </div>
              </div>
              <p className="text-sm text-muted-foreground">
                {prediction.data.businessExplanation}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Probabilities</CardTitle>
              <CardDescription>Class probability distribution.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {Object.entries(prediction.data.probabilities).map(([label, value]) => (
                <div key={label} className="space-y-1">
                  <div className="flex items-center justify-between text-sm">
                    <span>{label}</span>
                    <span className="text-muted-foreground">
                      {formatPercent(value)}
                    </span>
                  </div>
                  <div className="h-2 overflow-hidden rounded-full bg-muted">
                    <div
                      className="h-full rounded-full bg-primary"
                      style={{ width: `${value * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Top Features</CardTitle>
              <CardDescription>Highest model-weighted drivers.</CardDescription>
            </CardHeader>
            <CardContent>
              <DataTable>
                <DataTableHeader>
                  <DataTableRow>
                    <DataTableHead>Feature</DataTableHead>
                    <DataTableHead>Value</DataTableHead>
                    <DataTableHead>Weight</DataTableHead>
                  </DataTableRow>
                </DataTableHeader>
                <DataTableBody>
                  {prediction.data.topFeatures.map((feature) => (
                    <DataTableRow key={feature.name}>
                      <DataTableCell>{feature.name.replaceAll("_", " ")}</DataTableCell>
                      <DataTableCell>
                        {typeof feature.value === "number"
                          ? formatNumber(feature.value, 4)
                          : (feature.value ?? "Unknown")}
                      </DataTableCell>
                      <DataTableCell>
                        {formatNumber(feature.importance, 4)}
                      </DataTableCell>
                    </DataTableRow>
                  ))}
                </DataTableBody>
              </DataTable>
            </CardContent>
          </Card>
        </div>
      ) : null}
    </div>
  );
}
