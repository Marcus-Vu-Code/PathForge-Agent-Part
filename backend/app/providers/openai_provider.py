from __future__ import annotations

import json
import time
from typing import Any

from app.config import Settings
from app.models.schemas import (
    BackgroundArtifactExtraction,
    CareerPlan,
    CareerProfile,
    CareerReasoningRequest,
    CareerReasoningResult,
    EvidenceItem,
    UploadedArtifact,
)
from app.providers.base import ProviderContractError, ProviderUnavailableError
from app.providers.fake_provider import FakeBackgroundExtractor


EXTRACTION_PROMPT = """Extract a versioned CareerProfile from the submitted background.
Use only facts present in the artifact. Preserve uncertainty in warnings. Return JSON only."""

REASONING_PROMPT = """You are PathForge AI, a career-navigation reasoner.
Synthesize the supplied profile, goal, deterministic tool outputs, and evidence into a typed CareerPlan.
Do not invent user skills or market facts. Use caveats for uncertainty. Return JSON only."""


class OpenAIBackgroundExtractor:
    def __init__(self, settings: Settings, client: Any | None = None):
        self.settings = settings
        self.client = client

    def _client(self) -> Any:
        if self.client is not None:
            return self.client
        if not self.settings.openai_api_key:
            raise ProviderUnavailableError("OPENAI_API_KEY is not configured")
        try:
            from openai import AsyncOpenAI
        except ImportError as exc:
            raise ProviderUnavailableError("openai package is required for the OpenAI provider") from exc
        self.client = AsyncOpenAI(api_key=self.settings.openai_api_key, timeout=30)
        return self.client

    async def extract(self, artifact: UploadedArtifact) -> BackgroundArtifactExtraction:
        started = time.perf_counter()
        client = self._client()
        schema = BackgroundArtifactExtraction.model_json_schema()
        try:
            response = await client.responses.create(
                model=self.settings.openai_model,
                input=[
                    {"role": "system", "content": EXTRACTION_PROMPT},
                    {"role": "user", "content": artifact.model_dump_json()},
                ],
                text={"format": {"type": "json_schema", "name": "BackgroundArtifactExtraction", "schema": schema, "strict": True}},
            )
        except Exception as exc:
            raise ProviderUnavailableError(f"OpenAI extraction failed: {exc}") from exc

        payload = _response_text(response)
        try:
            parsed = BackgroundArtifactExtraction.model_validate_json(payload)
        except Exception as exc:
            raise ProviderContractError("OpenAI extraction returned an invalid schema") from exc
        parsed.warnings.append(f"OpenAI latency: {int((time.perf_counter() - started) * 1000)} ms")
        return parsed


class OpenAICareerReasoner:
    def __init__(self, settings: Settings, client: Any | None = None):
        self.settings = settings
        self.client = client

    def _client(self) -> Any:
        if self.client is not None:
            return self.client
        if not self.settings.openai_api_key:
            raise ProviderUnavailableError("OPENAI_API_KEY is not configured")
        try:
            from openai import AsyncOpenAI
        except ImportError as exc:
            raise ProviderUnavailableError("openai package is required for the OpenAI provider") from exc
        self.client = AsyncOpenAI(api_key=self.settings.openai_api_key, timeout=45)
        return self.client

    async def reason(self, request: CareerReasoningRequest) -> CareerReasoningResult:
        started = time.perf_counter()
        client = self._client()
        schema = CareerPlan.model_json_schema()
        tool_outputs: list[dict[str, Any]] = []
        tools = [
            {
                "type": "function",
                "name": "request_market_evidence",
                "description": "Request current role or market evidence when the supplied evidence is insufficient.",
                "parameters": {
                    "type": "object",
                    "properties": {"query": {"type": "string"}, "reason": {"type": "string"}},
                    "required": ["query", "reason"],
                    "additionalProperties": False,
                },
                "strict": True,
            },
            {"type": "web_search_preview"},
        ]
        response_input: list[dict[str, Any]] = [
            {"role": "system", "content": REASONING_PROMPT},
            {"role": "user", "content": request.model_dump_json()},
        ]

        try:
            for _ in range(3):
                response = await client.responses.create(
                    model=self.settings.openai_model,
                    input=response_input,
                    tools=tools,
                    text={"format": {"type": "json_schema", "name": "CareerPlan", "schema": schema, "strict": True}},
                )
                calls = _tool_calls(response)
                if not calls:
                    payload = _response_text(response)
                    plan = CareerPlan.model_validate_json(payload)
                    plan.evidence.extend(_extract_citations(response))
                    return CareerReasoningResult(
                        plan=plan,
                        provider="openai",
                        model_version=self.settings.openai_model,
                        latency_ms=int((time.perf_counter() - started) * 1000),
                        warnings=[f"tool_outputs_returned={len(tool_outputs)}"] if tool_outputs else [],
                    )
                for call in calls:
                    output = _handle_openai_tool_call(call)
                    tool_outputs.append(output)
                    response_input.append({"type": "function_call_output", "call_id": call["call_id"], "output": json.dumps(output)})
        except ProviderContractError:
            raise
        except Exception as exc:
            raise ProviderUnavailableError(f"OpenAI reasoning failed: {exc}") from exc

        raise ProviderContractError("OpenAI reasoning did not produce a final CareerPlan")


def _response_text(response: Any) -> str:
    if hasattr(response, "output_text") and response.output_text:
        return response.output_text
    if isinstance(response, dict) and response.get("output_text"):
        return response["output_text"]
    outputs = getattr(response, "output", None) or (response.get("output") if isinstance(response, dict) else None) or []
    for item in outputs:
        content = getattr(item, "content", None) or item.get("content", [])
        for block in content:
            text = getattr(block, "text", None) or block.get("text")
            if text:
                return text
    raise ProviderContractError("provider response did not include output text")


def _tool_calls(response: Any) -> list[dict[str, Any]]:
    outputs = getattr(response, "output", None) or (response.get("output") if isinstance(response, dict) else None) or []
    calls: list[dict[str, Any]] = []
    for item in outputs:
        item_type = getattr(item, "type", None) or item.get("type")
        if item_type == "function_call":
            calls.append(
                {
                    "call_id": getattr(item, "call_id", None) or item.get("call_id"),
                    "name": getattr(item, "name", None) or item.get("name"),
                    "arguments": getattr(item, "arguments", None) or item.get("arguments") or "{}",
                }
            )
    return calls


def _handle_openai_tool_call(call: dict[str, Any]) -> dict[str, Any]:
    if call["name"] != "request_market_evidence":
        return {"error": f"Unsupported tool call {call['name']}"}
    args = json.loads(call["arguments"])
    return {
        "query": args["query"],
        "note": "Use hosted web_search_preview results and preserve citations in CareerPlan.evidence.",
    }


def _extract_citations(response: Any) -> list[EvidenceItem]:
    evidence: list[EvidenceItem] = []
    outputs = getattr(response, "output", None) or (response.get("output") if isinstance(response, dict) else None) or []
    for item in outputs:
        content = getattr(item, "content", None) or item.get("content", [])
        for block in content:
            annotations = getattr(block, "annotations", None) or block.get("annotations", [])
            for annotation in annotations:
                url = getattr(annotation, "url", None) or annotation.get("url")
                title = getattr(annotation, "title", None) or annotation.get("title") or "OpenAI web citation"
                if url:
                    evidence.append(
                        EvidenceItem(
                            claim="OpenAI-hosted web search citation used by the plan.",
                            source_type="market",
                            source_title=title,
                            source_url=url,
                            confidence=0.75,
                        )
                    )
    return evidence


async def fallback_extraction(artifact: UploadedArtifact) -> BackgroundArtifactExtraction:
    return await FakeBackgroundExtractor().extract(artifact)

