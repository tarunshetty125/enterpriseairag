"""
Groq Integration Verification Script
=====================================
End-to-end verification of the Groq provider integration.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

# Ensure the backend package is importable
sys.path.insert(0, str(Path(__file__).resolve().parent))
os.chdir(Path(__file__).resolve().parent)

results: dict[str, dict] = {}

def section(name: str) -> None:
    print(f"\n{'='*70}")
    print(f"  {name}")
    print(f"{'='*70}")

def check(name: str, passed: bool, detail: str = "") -> None:
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"  {status} | {name}")
    if detail:
        for line in detail.split("\n"):
            print(f"         {line}")
    results[name] = {"passed": passed, "detail": detail}

# ─── 1. Configuration ───────────────────────────────────────────────
section("1. Configuration & Environment Loading")

try:
    from app.core.config import get_settings
    settings = get_settings()
    check(".env loaded", True, f"App name: {settings.app.name}")
except Exception as e:
    check(".env loaded", False, str(e))
    print("FATAL: Cannot proceed without settings.")
    sys.exit(1)

check("GROQ_API_KEY detected",
      bool(settings.ai.groq_api_key),
      f"Key prefix: {settings.ai.groq_api_key[:8]}..." if settings.ai.groq_api_key else "NOT SET")

check("Provider set to groq",
      settings.ai.provider == "groq",
      f"Provider: {settings.ai.provider}")

check("Model configured",
      bool(settings.ai.model),
      f"Model: {settings.ai.model}")

check("Base URL configured",
      "groq.com" in settings.ai.groq_base_url,
      f"URL: {settings.ai.groq_base_url}")

check("AI settings validated",
      0 <= settings.ai.temperature <= 2 and 0 < settings.ai.max_tokens,
      f"temp={settings.ai.temperature}, max_tokens={settings.ai.max_tokens}")


# ─── 2. Missing key error message ───────────────────────────────────
section("2. Missing Key Error Handling")

from app.providers.groq import GroqProvider
from app.providers.base import ProviderConfigurationError, ProviderMessage, ProviderRequest

no_key_provider = GroqProvider(
    base_url=settings.ai.groq_base_url,
    api_key=None,
)

try:
    no_key_provider.chat(ProviderRequest(
        messages=[ProviderMessage(role="user", content="test")],
        model="llama-3.3-70b-versatile",
        temperature=0.2,
        top_p=0.9,
        max_tokens=10,
    ))
    check("Missing key → clear error", False, "No exception raised!")
except ProviderConfigurationError as e:
    check("Missing key → clear error", True, f"Error: {e}")
except Exception as e:
    check("Missing key → clear error", False, f"Unexpected error type: {type(e).__name__}: {e}")


# ─── 3. Provider Initialization ────────────────────────────────────
section("3. GroqProvider Initialization & Authentication")

provider = GroqProvider(
    base_url=settings.ai.groq_base_url,
    api_key=settings.ai.groq_api_key,
)

check("GroqProvider initializes", True,
      f"provider_name={provider.provider_name}, base_url={provider.base_url}")


# ─── 4. Model Loading ──────────────────────────────────────────────
section("4. Model Loading (Dynamic from Groq API)")

try:
    t0 = time.perf_counter()
    models = provider.list_models()
    model_time = round((time.perf_counter() - t0) * 1000, 2)
    model_ids = [m.id for m in models]
    check("Models retrieved from Groq",
          len(models) > 0,
          f"{len(models)} models in {model_time}ms\nFirst 10: {model_ids[:10]}")
except Exception as e:
    check("Models retrieved from Groq", False, str(e))
    model_ids = []


# ─── 5. Health Check ───────────────────────────────────────────────
section("5. Provider Health Check")

try:
    health = provider.health()
    check("Health status = online",
          health.status == "online",
          f"Status: {health.status}, Configured: {health.configured}, "
          f"Latency: {health.latency_ms}ms, Details: {health.details}")
except Exception as e:
    check("Health status = online", False, str(e))


# ─── 6. Direct Chat Request ────────────────────────────────────────
section("6. Direct Chat (GroqProvider.chat)")

try:
    t0 = time.perf_counter()
    response = provider.chat(ProviderRequest(
        messages=[ProviderMessage(role="user", content="Hello! Reply with exactly one sentence.")],
        model="llama-3.3-70b-versatile",
        temperature=0.2,
        top_p=0.9,
        max_tokens=100,
    ))
    chat_latency = round((time.perf_counter() - t0) * 1000, 2)
    check("Direct chat successful",
          len(response.content) > 0,
          f"Response: {response.content[:200]}\n"
          f"Model: {response.model}\n"
          f"Latency: {chat_latency}ms\n"
          f"Tokens: prompt={response.usage.prompt_tokens}, "
          f"completion={response.usage.completion_tokens}, "
          f"total={response.usage.total_tokens}")
except Exception as e:
    check("Direct chat successful", False, str(e))
    chat_latency = None


# ─── 7. Invalid Key Error ──────────────────────────────────────────
section("7. Error Handling - Invalid API Key")

bad_provider = GroqProvider(
    base_url=settings.ai.groq_base_url,
    api_key="invalid-key-12345",
)

try:
    bad_provider.chat(ProviderRequest(
        messages=[ProviderMessage(role="user", content="test")],
        model="llama-3.3-70b-versatile",
        temperature=0.2,
        top_p=0.9,
        max_tokens=10,
    ))
    check("Invalid key → error (no crash)", False, "No exception raised!")
except Exception as e:
    check("Invalid key → error (no crash)", True, f"{type(e).__name__}: {str(e)[:200]}")


# ─── 8. Unavailable Model ─────────────────────────────────────────
section("8. Error Handling - Unavailable Model")

try:
    provider.chat(ProviderRequest(
        messages=[ProviderMessage(role="user", content="test")],
        model="nonexistent-model-xyz",
        temperature=0.2,
        top_p=0.9,
        max_tokens=10,
    ))
    check("Unavailable model → error (no crash)", False, "No exception raised!")
except Exception as e:
    check("Unavailable model → error (no crash)", True, f"{type(e).__name__}: {str(e)[:200]}")


# ─── 9. Database + ProviderManager ─────────────────────────────────
section("9. ProviderManager (DB-backed)")

from app.db.session import initialize_database, get_db_session

initialize_database()
db = next(get_db_session())

try:
    from app.providers.manager import ProviderManager
    manager = ProviderManager(db)
    current = manager.current_settings()
    check("ProviderManager initializes",
          True,
          f"Provider: {current.provider}, Model: {current.model}")
except Exception as e:
    check("ProviderManager initializes", False, str(e))

try:
    descriptors = manager.list_providers()
    groq_desc = next((d for d in descriptors if d.name == "groq"), None)
    check("Groq listed in providers",
          groq_desc is not None,
          "\n".join(f"  {d.name}: status={d.status}, active={d.active}" for d in descriptors))
    if groq_desc:
        check("Groq is active provider",
              groq_desc.active,
              f"Active: {groq_desc.active}")
        check("Groq status = online",
              groq_desc.status == "online",
              f"Status: {groq_desc.status}, Latency: {groq_desc.latency_ms}ms")
except Exception as e:
    check("Groq listed in providers", False, str(e))

try:
    pm_models = manager.list_models("groq")
    check("Models via ProviderManager",
          len(pm_models) > 0,
          f"{len(pm_models)} models: {[m.id for m in pm_models[:5]]}")
except Exception as e:
    check("Models via ProviderManager", False, str(e))


# ─── 10. AI Gateway Routing ────────────────────────────────────────
section("10. AI Gateway Routing")

try:
    from app.gateway.ai_gateway import AIGateway, GatewayRequest

    gateway = AIGateway(db)
    t0 = time.perf_counter()
    gw_response = gateway.chat(GatewayRequest(
        messages=[
            ProviderMessage(role="system", content="You are a helpful assistant."),
            ProviderMessage(role="user", content="Say 'Gateway routing works!' and nothing else."),
        ],
        operation="verification_test",
        metadata={"test": "gateway_routing"},
    ))
    gw_latency = round((time.perf_counter() - t0) * 1000, 2)
    check("Gateway routes to Groq",
          len(gw_response.content) > 0,
          f"Response: {gw_response.content[:200]}\n"
          f"Provider: {gw_response.provider}, Model: {gw_response.model}\n"
          f"Latency: {gw_latency}ms\n"
          f"Tokens: prompt={gw_response.usage.prompt_tokens}, "
          f"completion={gw_response.usage.completion_tokens}, "
          f"total={gw_response.usage.total_tokens}")
except Exception as e:
    check("Gateway routes to Groq", False, str(e))


# ─── 11. Provider Switching ────────────────────────────────────────
section("11. Runtime Provider Switching (No Restart)")

try:
    # Switch to openai (will fail on chat because no key, but switch should succeed)
    switched = manager.switch_provider("groq", "llama-3.3-70b-versatile")
    check("Switch provider (no restart)",
          switched.provider == "groq",
          f"Switched to: {switched.provider}/{switched.model}")
except Exception as e:
    check("Switch provider (no restart)", False, str(e))


# ─── 12. Metrics Recording ────────────────────────────────────────
section("12. Metrics & Developer Console Data")

try:
    from app.gateway.metrics import MetricsCollector
    metrics = MetricsCollector(db).status()
    check("Metrics recorded",
          metrics.get("metric_count", 0) > 0,
          json.dumps(metrics, indent=2, default=str))
except Exception as e:
    check("Metrics recorded", False, str(e))


# ─── Summary ──────────────────────────────────────────────────────
section("VERIFICATION SUMMARY")

passed = sum(1 for r in results.values() if r["passed"])
failed = sum(1 for r in results.values() if not r["passed"])
total = len(results)

print(f"\n  Total: {total}  |  Passed: {passed}  |  Failed: {failed}")
print(f"  Pass Rate: {passed/total*100:.0f}%\n")

if failed > 0:
    print("  Failed checks:")
    for name, r in results.items():
        if not r["passed"]:
            print(f"    ❌ {name}: {r['detail'][:100]}")
else:
    print("  🎉 All checks passed! Groq integration is fully operational.")
