"use client";

import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Settings2 } from "lucide-react";

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
  getAIProcessingSettings,
  getProviderModels,
  getProviders,
  getPrompts,
  patchProviderSettings,
  switchProvider,
} from "@/lib/api/platform";
import type { ProviderSettingsPatch } from "@/types/platform";

export function AIProcessingSettingsPanel() {
  const queryClient = useQueryClient();
  const settings = useQuery({
    queryKey: ["platform", "ai-processing-settings"],
    queryFn: getAIProcessingSettings,
  });
  const providers = useQuery({
    queryKey: ["providers"],
    queryFn: getProviders,
  });
  const prompts = useQuery({
    queryKey: ["prompts"],
    queryFn: getPrompts,
  });
  const [provider, setProvider] = useState("");
  const [model, setModel] = useState("");
  const models = useQuery({
    queryKey: ["providers", "models", provider],
    queryFn: () => getProviderModels(provider),
    enabled: Boolean(provider),
  });
  const [form, setForm] = useState<ProviderSettingsPatch>({});
  const providerSwitch = useMutation({
    mutationFn: () => switchProvider(provider, model),
    onSuccess: async () => {
      await queryClient.invalidateQueries();
    },
  });
  const settingsPatch = useMutation({
    mutationFn: () => patchProviderSettings(form),
    onSuccess: async () => {
      await queryClient.invalidateQueries();
    },
  });

  useEffect(() => {
    if (settings.data) {
      setProvider(settings.data.provider);
      setModel(settings.data.model);
      setForm({
        temperature: settings.data.temperature,
        topP: settings.data.topP,
        topK: settings.data.topK,
        maxTokens: settings.data.maxTokens,
        chunkSize: settings.data.chunkSize,
        embeddingModel: settings.data.embeddingModel,
        retrievalTopK: settings.data.retrievalTopK,
        similarityThreshold: settings.data.similarityThreshold,
        conversationMemory: settings.data.conversationMemory,
      });
    }
  }, [settings.data]);

  useEffect(() => {
    const firstModel = models.data?.models[0]?.id;
    if (firstModel && !models.data?.models.some((item) => item.id === model)) {
      setModel(firstModel);
    }
  }, [model, models.data?.models]);

  const updateNumber = (key: keyof ProviderSettingsPatch, value: string) => {
    setForm((current) => ({ ...current, [key]: Number(value) }));
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="AI Processing Settings"
        description="Runtime provider, model, generation, embedding, and retrieval controls."
      >
        <Badge variant="outline">{settings.data?.provider ?? "loading"}</Badge>
      </PageHeader>

      <div className="grid gap-6 xl:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Provider Management</CardTitle>
            <CardDescription>
              Switch providers and models without restarting FastAPI.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <label className="grid gap-2 text-sm">
              Provider
              <select
                className="h-9 rounded-md border bg-background px-3"
                value={provider}
                onChange={(event) => setProvider(event.target.value)}
              >
                {(providers.data?.providers ?? []).map((item) => (
                  <option key={item.name} value={item.name}>
                    {item.name} / {item.status}
                  </option>
                ))}
              </select>
            </label>
            <label className="grid gap-2 text-sm">
              Model
              <select
                className="h-9 rounded-md border bg-background px-3"
                value={model}
                onChange={(event) => setModel(event.target.value)}
              >
                {(models.data?.models ?? []).map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.name}
                  </option>
                ))}
              </select>
            </label>
            <Button
              disabled={!provider || !model || providerSwitch.isPending}
              onClick={() => providerSwitch.mutate()}
            >
              <Settings2 className="h-4 w-4" aria-hidden="true" />
              Apply Provider
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Generation Controls</CardTitle>
            <CardDescription>
              These settings are stored in SQLite and used by the AI Gateway.
            </CardDescription>
          </CardHeader>
          <CardContent className="grid gap-4 md:grid-cols-2">
            <NumberField
              label="Temperature"
              value={form.temperature}
              step="0.1"
              onChange={(value) => updateNumber("temperature", value)}
            />
            <NumberField
              label="Top-P"
              value={form.topP}
              step="0.05"
              onChange={(value) => updateNumber("topP", value)}
            />
            <NumberField
              label="Top-K"
              value={form.topK}
              onChange={(value) => updateNumber("topK", value)}
            />
            <NumberField
              label="Max Tokens"
              value={form.maxTokens}
              onChange={(value) => updateNumber("maxTokens", value)}
            />
            <NumberField
              label="Chunk Size"
              value={form.chunkSize}
              onChange={(value) => updateNumber("chunkSize", value)}
            />
            <NumberField
              label="Retrieval Top-K"
              value={form.retrievalTopK}
              onChange={(value) => updateNumber("retrievalTopK", value)}
            />
            <NumberField
              label="Similarity Threshold"
              value={form.similarityThreshold}
              step="0.01"
              onChange={(value) => updateNumber("similarityThreshold", value)}
            />
            <label className="grid gap-2 text-sm md:col-span-2">
              Embedding Model
              <input
                className="h-9 rounded-md border bg-background px-3"
                value={form.embeddingModel ?? ""}
                onChange={(event) =>
                  setForm((current) => ({
                    ...current,
                    embeddingModel: event.target.value,
                  }))
                }
              />
            </label>
            <label className="flex items-center gap-2 text-sm md:col-span-2">
              <input
                type="checkbox"
                checked={Boolean(form.conversationMemory)}
                onChange={(event) =>
                  setForm((current) => ({
                    ...current,
                    conversationMemory: event.target.checked,
                  }))
                }
              />
              Conversation memory
            </label>
            <Button
              className="md:col-span-2"
              disabled={settingsPatch.isPending}
              onClick={() => settingsPatch.mutate()}
            >
              Apply Settings
            </Button>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Prompt Versions</CardTitle>
          <CardDescription>
            Prompt templates are loaded by the backend prompt registry at
            request time, so template edits apply without a FastAPI restart.
          </CardDescription>
        </CardHeader>
        <CardContent className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          {(prompts.data ?? []).map((prompt) => (
            <div key={prompt.name} className="rounded-md border p-3 text-sm">
              <div className="font-medium">{prompt.name}</div>
              <div className="mt-1 text-xs text-muted-foreground">
                Version {prompt.version}
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}

function NumberField({
  label,
  value,
  step,
  onChange,
}: {
  label: string;
  value: number | undefined;
  step?: string;
  onChange: (value: string) => void;
}) {
  return (
    <label className="grid gap-2 text-sm">
      {label}
      <input
        className="h-9 rounded-md border bg-background px-3"
        type="number"
        step={step ?? "1"}
        value={value ?? ""}
        onChange={(event) => onChange(event.target.value)}
      />
    </label>
  );
}
