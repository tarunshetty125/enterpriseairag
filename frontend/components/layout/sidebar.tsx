"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { navigation } from "@/components/layout/navigation";
import { cn } from "@/lib/utils";

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed inset-y-0 left-0 z-30 hidden w-72 border-r bg-card/80 backdrop-blur lg:block">
      <div className="flex h-full flex-col">
        <div className="border-b px-6 py-5">
          <p className="text-xs font-medium uppercase tracking-[0.18em] text-muted-foreground">
            Enterprise AI
          </p>
          <h1 className="mt-2 text-lg font-semibold tracking-normal">
            Financial Intelligence
          </h1>
        </div>
        <nav className="flex flex-1 flex-col gap-1 px-3 py-4">
          {navigation.map((item) => {
            const isActive = pathname === item.href;
            const Icon = item.icon;

            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-muted-foreground transition-colors",
                  isActive && "bg-accent text-foreground",
                  !isActive && "hover:bg-accent hover:text-foreground",
                )}
              >
                <Icon className="h-4 w-4" aria-hidden="true" />
                {item.label}
              </Link>
            );
          })}
        </nav>
        <div className="border-t px-6 py-4 text-xs text-muted-foreground">
          Phase 1 foundation
        </div>
      </div>
    </aside>
  );
}
