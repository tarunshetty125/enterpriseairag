"use client";

import { Activity } from "lucide-react";

import { Badge } from "@/components/ui/badge";

export function TopNavigation() {
  return (
    <header className="sticky top-0 z-20 border-b bg-background/88 backdrop-blur">
      <div className="flex h-16 items-center justify-between px-4 sm:px-6 lg:px-8">
        <div className="flex items-center gap-3">
          <div>
            <p className="text-sm font-medium">AI Platform Workspace</p>
            <p className="text-xs text-muted-foreground">Local enterprise foundation</p>
          </div>
        </div>
        <Badge variant="secondary" className="gap-2">
          <Activity className="h-3.5 w-3.5" aria-hidden="true" />
          Phase 1
        </Badge>
      </div>
    </header>
  );
}
