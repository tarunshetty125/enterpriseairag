"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { PageHeader } from "@/components/layout/page-header";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { getPrompts } from "@/lib/api/platform";

export function PromptExplorerPanel() {
  const prompts = useQuery({
    queryKey: ["prompts"],
    queryFn: getPrompts,
  });
  const [selected, setSelected] = useState("rag_chat");
  const active =
    prompts.data?.find((prompt) => prompt.name === selected) ?? prompts.data?.[0];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Prompt Explorer"
        description="Versioned prompt templates used by the AI Gateway workflows."
      >
        <Badge variant="outline">{active?.version ?? "no prompts"}</Badge>
      </PageHeader>

      <div className="grid gap-6 xl:grid-cols-[320px_1fr]">
        <Card>
          <CardHeader>
            <CardTitle>Prompt Registry</CardTitle>
            <CardDescription>Templates are loaded from backend files.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            {(prompts.data ?? []).map((prompt) => (
              <button
                key={prompt.name}
                className="w-full rounded-md border p-3 text-left text-sm hover:bg-muted"
                type="button"
                onClick={() => setSelected(prompt.name)}
              >
                <div className="font-medium">{prompt.name}</div>
                <div className="text-xs text-muted-foreground">
                  {prompt.version} / {prompt.variables.join(", ")}
                </div>
              </button>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>{active?.name ?? "Select a prompt"}</CardTitle>
            <CardDescription>{active?.description ?? ""}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex flex-wrap gap-2">
              {(active?.variables ?? []).map((variable) => (
                <Badge key={variable} variant="secondary">
                  {variable}
                </Badge>
              ))}
            </div>
            <pre className="overflow-auto rounded-md border bg-muted p-4 text-sm leading-6">
              {active?.body ?? ""}
            </pre>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
