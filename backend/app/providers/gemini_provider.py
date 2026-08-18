from __future__ import annotations

import time
from typing import Any, TypeVar

from pydantic import BaseModel

from app.config import Settings
from app.models.schemas import (
    BackgroundArtifactExtraction,
    CareerPlan,
    CareerReasoningRequest,
    CareerReasoningResult,
    UploadedArtifact,
)
from app.providers.base import ProviderContractError, ProviderUnavailableError
from app.providers.openai_provider import EXTRACTION_PROMPT, REASONING_PROMPT

T = TypeVar("T", bound=BaseModel)


class GeminiBackgroundExtractor:
    """Gemini extractor using Google's OpenAI-compatible chat completions API."""

    def __init__(self, settings: Settings, client: Any | None = None):
        self.settings = settings
        self.client = client

    def _client(self) -> Any:
        if self.client is not None:
            return self.client
        if not self.settings.gemini_api_key:
            raise ProviderUnavailableError("GEMINI_API_KEY is not configured")
        try:
            from openai import AsyncOpenAI
        except ImportError as exc:
            raise ProviderUnavailableError("openai package is required for the Gemini compatibility provider") from exc
        self.client = AsyncOpenAI(
            api_key=self.settings.gemini_api_key,
            base_url=self.settings.gemini_base_url,
            timeout=30,
        )
        return self.client

    async def extract(self, artifact: UploadedArtifact) -> BackgroundArtifactExtraction:
        started = time.perf_counter()
        try:
            completion = await self._client().beta.chat.completions.parse(
                model=self.settings.gemini_model,
                messages=[
                    {"role": "system", "content": EXTRACTION_PROMPT},
                    {"role": "user", "content": artifact.model_dump_json()},
                ],
                response_format=BackgroundArtifactExtraction,
            )
            parsed = _parsed_message(completion, BackgroundArtifactExtraction)
        except ProviderContractError:
            raise
        except Exception as exc:
            raise ProviderUnavailableError(f"Gemini extraction failed: {exc}") from exc
        parsed.warnings.append(f"Gemini latency: {int((time.perf_counter() - started) * 1000)} ms")
        return parsed


class GeminiCareerReasoner:
    """Gemini reasoner behind the CareerReasoner protocol."""

    def __init__(self, settings: Settings, client: Any | None = None):
        self.settings = settings
        self.client = client

    def _client(self) -> Any:
        if self.client is not None:
            return self.client
        if not self.settings.gemini_api_key:
            raise ProviderUnavailableError("GEMINI_API_KEY is not configured")
        try:
            from openai import AsyncOpenAI
        except ImportError as exc:
            raise ProviderUnavailableError("openai package is required for the Gemini compatibility provider") from exc
        self.client = AsyncOpenAI(
            api_key=self.settings.gemini_api_key,
            base_url=self.settings.gemini_base_url,
            timeout=45,
        )
        return self.client

    async def reason(self, request: CareerReasoningRequest) -> CareerReasoningResult:
        started = time.perf_counter()
        try:
            completion = await self._client().beta.chat.completions.parse(
                model=self.settings.gemini_model,
                messages=[
                    {"role": "system", "content": REASONING_PROMPT},
                    {"role": "user", "content": request.model_dump_json()},
                ],
                response_format=CareerPlan,
            )
            plan = _parsed_message(completion, CareerPlan)
        except ProviderContractError:
            raise
        except Exception as exc:
            raise ProviderUnavailableError(f"Gemini reasoning failed: {exc}") from exc
        return CareerReasoningResult(
            plan=plan,
            provider="gemini",
            model_version=self.settings.gemini_model,
            latency_ms=int((time.perf_counter() - started) * 1000),
        )


def _parsed_message(completion: Any, schema: type[T]) -> T:
    try:
        message = completion.choices[0].message
    except Exception as exc:
        raise ProviderContractError("Gemini response did not include a chat completion message") from exc

    parsed = getattr(message, "parsed", None)
    if parsed is not None:
        return parsed

    content = getattr(message, "content", None)
    if not content:
        raise ProviderContractError("Gemini response did not include parsed JSON content")
    try:
        return schema.model_validate_json(content)
    except Exception as exc:
        raise ProviderContractError("Gemini response did not match the requested schema") from exc

