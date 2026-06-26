import * as React from "react";

import { cn } from "@/lib/utils";

export function DataTable({ children }: { children: React.ReactNode }) {
  return (
    <div className="overflow-hidden rounded-lg border">
      <div className="overflow-x-auto">
        <table className="w-full text-sm">{children}</table>
      </div>
    </div>
  );
}

export function DataTableHeader({ children }: { children: React.ReactNode }) {
  return <thead className="bg-muted/60 text-muted-foreground">{children}</thead>;
}

export function DataTableBody({ children }: { children: React.ReactNode }) {
  return <tbody className="divide-y divide-border">{children}</tbody>;
}

export function DataTableRow({ children }: { children: React.ReactNode }) {
  return <tr className="transition-colors hover:bg-muted/30">{children}</tr>;
}

export function DataTableHead({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <th className={cn("px-4 py-3 text-left text-xs font-medium", className)}>
      {children}
    </th>
  );
}

export function DataTableCell({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return <td className={cn("px-4 py-3 align-top", className)}>{children}</td>;
}
