"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Database, RefreshCw } from "lucide-react";

import { StatusCard } from "@/components/dashboard/status-card";
import { PageHeader } from "@/components/layout/page-header";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  DataTable,
  DataTableBody,
  DataTableCell,
  DataTableHead,
  DataTableHeader,
  DataTableRow,
} from "@/components/ui/data-table";
import {
  getKnowledgeDocuments,
  getKnowledgeStatus,
  ingestKnowledge,
} from "@/lib/api/platform";

export function KnowledgeBasePanel() {
  const queryClient = useQueryClient();
  const status = useQuery({
    queryKey: ["knowledge", "status"],
    queryFn: getKnowledgeStatus,
  });
  const documents = useQuery({
    queryKey: ["knowledge", "documents"],
    queryFn: getKnowledgeDocuments,
  });
  const ingest = useMutation({
    mutationFn: ingestKnowledge,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["knowledge"] });
      await queryClient.invalidateQueries({ queryKey: ["platform", "knowledge-status"] });
    },
  });

  return (
    <div className="space-y-6">
      <PageHeader
        title="Knowledge Base"
        description="Banking policy documents, chunks, embeddings, and vector index status."
      >
        <Badge variant="outline">{status.data?.vectorBackend ?? "not indexed"}</Badge>
      </PageHeader>

      <div className="grid gap-4 md:grid-cols-4">
        <StatusCard title="Documents" value={status.data?.documentCount ?? 0} />
        <StatusCard title="Chunks" value={status.data?.chunkCount ?? 0} />
        <StatusCard
          title="Index Size"
          value={status.data?.faissIndexSize ?? 0}
        />
        <StatusCard
          title="Embedding"
          value={status.data?.embeddingBackend ?? "unavailable"}
        />
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between gap-4">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Database className="h-4 w-4" aria-hidden="true" />
              Indexed Documents
            </CardTitle>
            <CardDescription>
              Ingestion reads local files from the policies directory.
            </CardDescription>
          </div>
          <Button disabled={ingest.isPending} onClick={() => ingest.mutate()}>
            <RefreshCw className="h-4 w-4" aria-hidden="true" />
            Ingest
          </Button>
        </CardHeader>
        <CardContent>
          <DataTable>
            <DataTableHeader>
              <DataTableRow>
                <DataTableHead>Document</DataTableHead>
                <DataTableHead>Type</DataTableHead>
                <DataTableHead>Chunks</DataTableHead>
                <DataTableHead>Version</DataTableHead>
                <DataTableHead>Indexed</DataTableHead>
              </DataTableRow>
            </DataTableHeader>
            <DataTableBody>
              {(documents.data ?? []).map((document) => (
                <DataTableRow key={document.id}>
                  <DataTableCell>{document.documentName}</DataTableCell>
                  <DataTableCell>{document.documentType}</DataTableCell>
                  <DataTableCell>{document.chunkCount}</DataTableCell>
                  <DataTableCell>{document.version}</DataTableCell>
                  <DataTableCell>
                    {new Date(document.indexedAt).toLocaleString()}
                  </DataTableCell>
                </DataTableRow>
              ))}
            </DataTableBody>
          </DataTable>
        </CardContent>
      </Card>
    </div>
  );
}
