import { BarChart3, Bot, Gauge, LayoutDashboard, Settings, Users } from "lucide-react";
import type { LucideIcon } from "lucide-react";

export interface NavigationItem {
  label: string;
  href: string;
  icon: LucideIcon;
}

export const navigation: NavigationItem[] = [
  { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { label: "Customers", href: "/customers", icon: Users },
  { label: "Analytics", href: "/analytics", icon: BarChart3 },
  { label: "AI Assistant", href: "/assistant", icon: Bot },
  { label: "Developer Console", href: "/developer-console", icon: Gauge },
  { label: "Settings", href: "/settings", icon: Settings },
];
