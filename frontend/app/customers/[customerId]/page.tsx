import { CustomerDetailPanel } from "@/components/customer/customer-detail-panel";

export default async function CustomerDetailPage({
  params,
}: {
  params: Promise<{ customerId: string }>;
}) {
  const { customerId } = await params;
  return <CustomerDetailPanel customerId={customerId} />;
}
