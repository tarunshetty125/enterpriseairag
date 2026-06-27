from __future__ import annotations

from fastapi.testclient import TestClient


def test_phase5_provider_prompt_knowledge_and_chat_api(client: TestClient) -> None:
    providers = client.get("/api/v1/providers")
    assert providers.status_code == 200
    provider_names = {item["name"] for item in providers.json()["providers"]}
    assert {"groq", "openai", "gemini", "ollama", "anthropic"} <= provider_names

    models = client.get("/api/v1/providers/models", params={"provider": "openai"})
    assert models.status_code == 200
    assert any(model["id"] == "gpt-4o" for model in models.json()["models"])

    switch = client.post(
        "/api/v1/providers/switch",
        json={"provider": "openai", "model": "gpt-4o"},
    )
    assert switch.status_code == 200
    assert switch.json()["provider"] == "openai"
    assert switch.json()["model"] == "gpt-4o"

    settings = client.patch(
        "/api/v1/providers/settings",
        json={"similarityThreshold": 0.0, "retrievalTopK": 3},
    )
    assert settings.status_code == 200
    assert settings.json()["retrievalTopK"] == 3

    prompts = client.get("/api/v1/prompts")
    assert prompts.status_code == 200
    assert any(prompt["name"] == "rag_chat" for prompt in prompts.json())

    ingest = client.post("/api/v1/knowledge/ingest")
    assert ingest.status_code == 200
    assert ingest.json()["documentsIndexed"] >= 1
    assert ingest.json()["chunksIndexed"] >= 1

    knowledge_status = client.get("/api/v1/knowledge/status")
    assert knowledge_status.status_code == 200
    assert knowledge_status.json()["chunkCount"] >= 1

    chat = client.post(
        "/api/v1/chat",
        json={"message": "Summarize the home loan eligibility rules."},
    )
    assert chat.status_code == 200
    payload = chat.json()
    assert payload["sessionId"]
    assert payload["retrievedChunks"] >= 1
    assert payload["citations"]
    assert payload["status"] in {"success", "provider_not_configured"}

    sessions = client.get("/api/v1/chat/sessions")
    assert sessions.status_code == 200
    assert sessions.json()
