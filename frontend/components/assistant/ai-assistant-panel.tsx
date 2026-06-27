"use client";

import { FormEvent, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Bot, Send } from "lucide-react";

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
import { getChatSessions, sendChatMessage } from "@/lib/api/platform";
import type { ChatResponse } from "@/types/platform";

interface LocalMessage {
  role: "user" | "assistant";
  content: string;
  response?: ChatResponse;
}

export function AIAssistantPanel() {
  const [sessionId, setSessionId] = useState<string | undefined>();
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<LocalMessage[]>([]);
  const sessions = useQuery({
    queryKey: ["chat", "sessions"],
    queryFn: getChatSessions,
  });
  const chat = useMutation({
    mutationFn: () => sendChatMessage(message, sessionId),
    onSuccess: (response) => {
      setSessionId(response.sessionId);
      setMessages((current) => [
        ...current,
        { role: "user", content: message },
        { role: "assistant", content: response.answer, response },
      ]);
      setMessage("");
    },
  });

  const submit = (event: FormEvent) => {
    event.preventDefault();
    if (message.trim()) {
      chat.mutate();
    }
  };

  const latest = messages.findLast((item) => item.response)?.response;

  return (
    <div className="space-y-6">
      <PageHeader
        title="AI Assistant"
        description="Grounded policy assistant restricted to banking documentation and citations."
      >
        <Badge variant="outline">{latest?.provider ?? "policy assistant"}</Badge>
      </PageHeader>

      <div className="grid gap-6 xl:grid-cols-[1fr_360px]">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Bot className="h-4 w-4" aria-hidden="true" />
              Conversation
            </CardTitle>
            <CardDescription>
              Ask about indexed policies. Unsupported questions return insufficient evidence.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="min-h-[360px] space-y-3 rounded-md border p-4">
              {messages.map((item, index) => (
                <div
                  key={`${item.role}-${index}`}
                  className={
                    item.role === "user"
                      ? "ml-auto max-w-[80%] rounded-md bg-primary p-3 text-sm text-primary-foreground"
                      : "max-w-[85%] rounded-md bg-muted p-3 text-sm"
                  }
                >
                  <p className="whitespace-pre-wrap">{item.content}</p>
                  {item.response ? (
                    <div className="mt-3 flex flex-wrap gap-2 text-xs">
                      <Badge variant="outline">{item.response.status}</Badge>
                      <Badge variant="outline">
                        {item.response.retrievedChunks} chunks
                      </Badge>
                      <Badge variant="outline">
                        {item.response.latencyMs.toFixed(1)} ms
                      </Badge>
                    </div>
                  ) : null}
                </div>
              ))}
            </div>
            <form className="flex gap-2" onSubmit={submit}>
              <input
                className="h-10 flex-1 rounded-md border bg-background px-3 text-sm"
                value={message}
                onChange={(event) => setMessage(event.target.value)}
                placeholder="Summarize the home loan eligibility rules."
              />
              <Button disabled={chat.isPending || !message.trim()} type="submit">
                <Send className="h-4 w-4" aria-hidden="true" />
                Send
              </Button>
            </form>
          </CardContent>
        </Card>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Runtime Metrics</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <Metric label="Provider" value={latest?.provider ?? "Unavailable"} />
              <Metric label="Model" value={latest?.model ?? "Unavailable"} />
              <Metric
                label="Prompt Version"
                value={latest?.promptVersion ?? "Unavailable"}
              />
              <Metric
                label="Token Usage"
                value={String(latest?.tokenUsage.totalTokens ?? 0)}
              />
              <Metric
                label="Context Size"
                value={String(latest?.contextSize ?? 0)}
              />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Source Citations</CardTitle>
            </CardHeader>
            <CardContent>
              <DataTable>
                <DataTableHeader>
                  <DataTableRow>
                    <DataTableHead>Document</DataTableHead>
                    <DataTableHead>Chunk</DataTableHead>
                    <DataTableHead>Score</DataTableHead>
                  </DataTableRow>
                </DataTableHeader>
                <DataTableBody>
                  {(latest?.citations ?? []).map((citation) => (
                    <DataTableRow key={`${citation.document}-${citation.chunk}`}>
                      <DataTableCell>{citation.document}</DataTableCell>
                      <DataTableCell>{citation.chunk}</DataTableCell>
                      <DataTableCell>
                        {citation.similarityScore.toFixed(3)}
                      </DataTableCell>
                    </DataTableRow>
                  ))}
                </DataTableBody>
              </DataTable>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Chat History</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {(sessions.data ?? []).slice(0, 8).map((session) => (
                <button
                  key={session.sessionId}
                  className="w-full rounded-md border p-3 text-left text-sm hover:bg-muted"
                  type="button"
                  onClick={() => setSessionId(session.sessionId)}
                >
                  <div className="font-medium">{session.title}</div>
                  <div className="text-xs text-muted-foreground">
                    {session.provider} / {session.model}
                  </div>
                </button>
              ))}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between gap-3">
      <span className="text-muted-foreground">{label}</span>
      <span className="text-right font-medium">{value}</span>
    </div>
  );
}
