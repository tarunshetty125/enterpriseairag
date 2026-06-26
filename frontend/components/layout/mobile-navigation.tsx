"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { navigation } from "@/components/layout/navigation";
import { cn } from "@/lib/utils";

export function MobileNavigation() {
  const pathname = usePathname();

  return (
    <nav className="border-b bg-card/70 px-4 py-2 backdrop-blur lg:hidden">
      <div className="flex gap-2 overflow-x-auto">
        {navigation.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex shrink-0 items-center gap-2 rounded-md px-3 py-2 text-xs font-medium text-muted-foreground transition-colors",
                isActive && "bg-accent text-foreground",
                !isActive && "hover:bg-accent hover:text-foreground",
              )}
            >
              <Icon className="h-4 w-4" aria-hidden="true" />
              {item.label}
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
