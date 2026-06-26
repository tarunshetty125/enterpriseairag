import {
  BarChart3,
  Bot,
  Database,
  Gauge,
  Layers3,
  LayoutDashboard,
  Settings,
  ShieldCheck,
  Users,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";

export interface NavigationItem {
  label: string;
  href: string;
  icon: LucideIcon;
}

export const navigation: NavigationItem[] = [
  { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { label: "Datasets", href: "/datasets", icon: Database },
  { label: "Customers", href: "/customers", icon: Users },
  { label: "Feature Store", href: "/feature-store", icon: Layers3 },
  { label: "Data Quality", href: "/data-quality", icon: ShieldCheck },
  { label: "Analytics", href: "/analytics", icon: BarChart3 },
  { label: "AI Assistant", href: "/assistant", icon: Bot },
  { label: "Developer Console", href: "/developer-console", icon: Gauge },
  { label: "Settings", href: "/settings", icon: Settings },
];
