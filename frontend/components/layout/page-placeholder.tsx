import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { PageHeader } from "@/components/layout/page-header";

export function PagePlaceholder({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <div className="space-y-6">
      <PageHeader title={title} description={description} />
      <Card>
        <CardHeader>
          <CardTitle>Phase 1 route shell</CardTitle>
          <CardDescription>
            This page is intentionally limited to the enterprise layout foundation.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Feature workflows will be connected in their approved phases after the
            backend services are implemented.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
