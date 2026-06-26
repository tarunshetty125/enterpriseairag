import * as React from "react";

import { Breadcrumbs } from "@/components/layout/breadcrumbs";
import { MobileNavigation } from "@/components/layout/mobile-navigation";
import { Sidebar } from "@/components/layout/sidebar";
import { TopNavigation } from "@/components/layout/top-navigation";

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-dvh bg-background">
      <Sidebar />
      <div className="min-h-dvh lg:pl-72">
        <TopNavigation />
        <MobileNavigation />
        <main className="mx-auto flex w-full max-w-7xl flex-col gap-6 px-4 py-6 sm:px-6 lg:px-8">
          <Breadcrumbs />
          {children}
        </main>
      </div>
    </div>
  );
}
