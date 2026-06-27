import {
  BarChart3,
  Bot,
  Boxes,
  Brain,
  Database,
  Gauge,
  Layers3,
  LayoutDashboard,
  LineChart,
  ListChecks,
  Settings,
  ShieldCheck,
  Sparkles,
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
  { label: "ML Dashboard", href: "/analytics", icon: BarChart3 },
  { label: "Model Registry", href: "/model-registry", icon: Brain },
  { label: "Risk Prediction", href: "/risk-prediction", icon: Gauge },
  { label: "Segmentation", href: "/segmentation", icon: Boxes },
  {
    label: "Transaction Intelligence",
    href: "/transaction-intelligence",
    icon: LineChart,
  },
  { label: "Behaviour", href: "/behaviour", icon: ListChecks },
  { label: "Recommendations", href: "/recommendations", icon: Sparkles },
  { label: "AI Assistant", href: "/assistant", icon: Bot },
  { label: "Developer Console", href: "/developer-console", icon: Gauge },
  { label: "Settings", href: "/settings", icon: Settings },
];
