"use client";

import { Database, Server, Settings2, Workflow } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PageHeader } from "@/components/layout/page-header";
import { usePlatformStatus } from "@/hooks/use-platform-status";

function statusLabel(isSuccess: boolean, isLoading: boolean) {
  if (isLoading) {
    return "Checking";
  }
  return isSuccess ? "Online" : "Offline";
}

export function DeveloperConsolePanel() {
  const { health, systemHealth, aiSettings } = usePlatformStatus();
  const sqlite = systemHealth.data?.components.find((item) => item.name === "sqlite");

  const cards = [
    {
      label: "Backend Status",
      value: statusLabel(health.isSuccess, health.isLoading),
      detail: health.data?.application ?? health.error?.message ?? "Waiting for API",
      icon: Server,
    },
    {
      label: "SQLite Status",
      value:
        sqlite?.status ?? statusLabel(systemHealth.isSuccess, systemHealth.isLoading),
      detail: sqlite?.details ?? "Database health endpoint pending",
      icon: Database,
    },
    {
      label: "Current AI Provider",
      value: aiSettings.data?.provider ?? "Unavailable",
      detail: "Configuration only in Phase 1",
      icon: Workflow,
    },
    {
      label: "Current Model",
      value: aiSettings.data?.model ?? "Unavailable",
      detail: `Version ${health.data?.version ?? "unknown"}`,
      icon: Settings2,
    },
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Developer Console"
        description="Phase 1 operational view backed by live health and configuration endpoints."
      >
        <Badge variant="outline">{health.data?.environment ?? "local"}</Badge>
      </PageHeader>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {cards.map((card) => {
          const Icon = card.icon;

          return (
            <Card key={card.label}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {card.label}
                </CardTitle>
                <Icon className="h-4 w-4 text-muted-foreground" aria-hidden="true" />
              </CardHeader>
              <CardContent className="space-y-2">
                <p className="text-xl font-semibold tracking-normal">{card.value}</p>
                <p className="text-xs text-muted-foreground">{card.detail}</p>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
