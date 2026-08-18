from __future__ import annotations

import time

from pydantic import BaseModel, ConfigDict

from app.config import Settings
from app.models.schemas import (
    BackgroundArtifactExtraction,
    CareerPlan,
    CareerReasoningRequest,
    CareerReasoningResult,
    RoutingTrace,
    UploadedArtifact,
)
from app.providers.base import ProviderContractError, ProviderUnavailableError


class LocalModelTrace(BaseModel):
    model_config = ConfigDict(extra="allow")
    model_version: str | None = None
    latency_ms: int = 0
    warnings: list[str] = []


class LocalCareerReasoningResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    plan: CareerPlan
    routing_trace: RoutingTrace | None = None
    model_trace: LocalModelTrace = LocalModelTrace()


class LocalMultimodalExtractor:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def extract(self, artifact: UploadedArtifact) -> BackgroundArtifactExtraction:
        try:
            import httpx
        except ImportError as exc:
            raise ProviderUnavailableError("httpx is required for the local provider") from exc

        try:
            async with httpx.AsyncClient(timeout=self.settings.local_model_timeout_seconds) as client:
                response = await client.post(
                    f"{self.settings.local_model_base_url}/v1/background/extract",
                    json=artifact.model_dump(mode="json"),
                )
                response.raise_for_status()
        except TimeoutError as exc:
            raise ProviderUnavailableError("local background extractor timed out") from exc
        except Exception as exc:
            raise ProviderUnavailableError(f"local background extractor unavailable: {exc}") from exc

        try:
            return BackgroundArtifactExtraction.model_validate(response.json())
        except Exception as exc:
            raise ProviderContractError("local background extractor returned an invalid schema") from exc


class LocalMoLECareerReasoner:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def health(self) -> dict:
        try:
            import httpx
        except ImportError as exc:
            raise ProviderUnavailableError("httpx is required for the local provider") from exc
        try:
            async with httpx.AsyncClient(timeout=self.settings.local_model_timeout_seconds) as client:
                response = await client.get(f"{self.settings.local_model_base_url}/health")
                response.raise_for_status()
                return response.json()
        except Exception as exc:
            raise ProviderUnavailableError(f"local provider health check failed: {exc}") from exc

    async def capabilities(self) -> dict:
        try:
            import httpx
        except ImportError as exc:
            raise ProviderUnavailableError("httpx is required for the local provider") from exc
        try:
            async with httpx.AsyncClient(timeout=self.settings.local_model_timeout_seconds) as client:
                response = await client.get(f"{self.settings.local_model_base_url}/v1/capabilities")
                response.raise_for_status()
                return response.json()
        except Exception as exc:
            raise ProviderUnavailableError(f"local provider capabilities check failed: {exc}") from exc

    async def reason(self, request: CareerReasoningRequest) -> CareerReasoningResult:
        try:
            import httpx
        except ImportError as exc:
            raise ProviderUnavailableError("httpx is required for the local provider") from exc

        started = time.perf_counter()
        payload = request.model_dump(mode="json")
        payload["generation"] = {"max_output_tokens": 1800}
        try:
            async with httpx.AsyncClient(timeout=self.settings.local_model_timeout_seconds) as client:
                response = await client.post(
                    f"{self.settings.local_model_base_url}/v1/career/reason",
                    json=payload,
                )
                response.raise_for_status()
        except TimeoutError as exc:
            raise ProviderUnavailableError("local career reasoner timed out") from exc
        except Exception as exc:
            raise ProviderUnavailableError(f"local career reasoner unavailable: {exc}") from exc

        try:
            parsed = LocalCareerReasoningResponse.model_validate(response.json())
        except Exception as exc:
            raise ProviderContractError("local career reasoner returned an invalid schema") from exc

        latency = parsed.model_trace.latency_ms or int((time.perf_counter() - started) * 1000)
        return CareerReasoningResult(
            plan=parsed.plan,
            provider="local",
            model_version=parsed.model_trace.model_version,
            latency_ms=latency,
            routing_trace=parsed.routing_trace,
            warnings=parsed.model_trace.warnings,
        )

