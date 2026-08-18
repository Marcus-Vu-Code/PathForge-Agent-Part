from __future__ import annotations

import asyncio
import json
import logging
import time
from functools import lru_cache
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
logger = logging.getLogger(__name__)


class QwenTransformersClient:
    """Lazy local Transformers runner for Qwen chat models."""

    def __init__(self, settings: Settings):
        self.settings = settings

    def generate(self, messages: list[dict[str, str]], max_new_tokens: int | None = None) -> str:
        tokenizer, model, torch = _load_qwen_model(
            self.settings.qwen_model,
            self.settings.qwen_device_map,
            self.settings.qwen_torch_dtype,
        )
        inputs = tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
        ).to(model.device)
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens or self.settings.qwen_max_new_tokens,
                do_sample=False,
                pad_token_id=tokenizer.eos_token_id,
            )
        generated = outputs[0][inputs["input_ids"].shape[-1] :]
        return tokenizer.decode(generated, skip_special_tokens=True)


class QwenBackgroundExtractor:
    def __init__(self, settings: Settings, client: Any | None = None):
        self.settings = settings
        self.client = client or QwenTransformersClient(settings)

    async def extract(self, artifact: UploadedArtifact) -> BackgroundArtifactExtraction:
        started = time.perf_counter()
        schema = BackgroundArtifactExtraction.model_json_schema()
        artifact_for_qwen, input_warnings = _limit_artifact_for_qwen(artifact, self.settings.qwen_max_input_chars)
        messages = [
            {
                "role": "system",
                "content": (
                    f"{EXTRACTION_PROMPT}\n"
                    "Return one JSON object that validates against this JSON schema:\n"
                    f"{json.dumps(schema)}"
                ),
            },
            {"role": "user", "content": artifact_for_qwen.model_dump_json()},
        ]
        text = await _generate_text(self.client, messages, self.settings.qwen_max_new_tokens)
        parsed = _parse_model_json(text, BackgroundArtifactExtraction)
        parsed.warnings.extend(input_warnings)
        parsed.warnings.append(f"Qwen Transformers latency: {int((time.perf_counter() - started) * 1000)} ms")
        return parsed


class QwenCareerReasoner:
    def __init__(self, settings: Settings, client: Any | None = None):
        self.settings = settings
        self.client = client or QwenTransformersClient(settings)

    async def reason(self, request: CareerReasoningRequest) -> CareerReasoningResult:
        started = time.perf_counter()
        schema = CareerPlan.model_json_schema()
        messages = [
            {
                "role": "system",
                "content": (
                    f"{REASONING_PROMPT}\n"
                    "Return one JSON object only. It must validate against this JSON schema:\n"
                    f"{json.dumps(schema)}"
                ),
            },
            {"role": "user", "content": request.model_dump_json()},
        ]
        text = await _generate_text(self.client, messages, self.settings.qwen_max_new_tokens)
        plan = _parse_model_json(text, CareerPlan)
        plan.caveats.append("Generated locally with Qwen/Qwen3-4B-Instruct-2507 through Hugging Face Transformers.")
        return CareerReasoningResult(
            plan=plan,
            provider="qwen",
            model_version=self.settings.qwen_model,
            latency_ms=int((time.perf_counter() - started) * 1000),
        )


async def _generate_text(client: Any, messages: list[dict[str, str]], max_new_tokens: int) -> str:
    try:
        logger.warning("Qwen generation started with max_new_tokens=%d", max_new_tokens)
        started = time.perf_counter()
        text = await asyncio.to_thread(client.generate, messages, max_new_tokens)
        logger.warning("Qwen generation finished in %d ms", int((time.perf_counter() - started) * 1000))
        return text
    except ProviderUnavailableError:
        raise
    except Exception as exc:
        raise ProviderUnavailableError(f"Qwen Transformers generation failed: {exc}") from exc


@lru_cache(maxsize=2)
def _load_qwen_model(model_name: str, device_map: str, torch_dtype: str):
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError as exc:
        raise ProviderUnavailableError("Install requirements-qwen.txt to use the Qwen Transformers provider") from exc

    if torch.cuda.is_available():
        logger.info("Qwen Transformers using CUDA device: %s", torch.cuda.get_device_name(0))
    else:
        logger.warning("Qwen Transformers is using CPU-only PyTorch. Install a CUDA PyTorch wheel for GPU inference.")

    logger.info("Loading Qwen model %s with device_map=%s dtype=%s", model_name, device_map, torch_dtype)
    started = time.perf_counter()
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    dtype = _resolve_torch_dtype(torch, torch_dtype)
    try:
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            dtype=dtype,
            device_map=device_map,
        )
    except TypeError:
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=dtype,
            device_map=device_map,
        )
    logger.info("Loaded Qwen model in %d ms", int((time.perf_counter() - started) * 1000))
    return tokenizer, model, torch


def _resolve_torch_dtype(torch: Any, torch_dtype: str):
    normalized = torch_dtype.lower().strip()
    if normalized == "auto":
        return "auto"
    dtype_map = {
        "float16": torch.float16,
        "fp16": torch.float16,
        "bfloat16": torch.bfloat16,
        "bf16": torch.bfloat16,
        "float32": torch.float32,
        "fp32": torch.float32,
    }
    if normalized not in dtype_map:
        raise ProviderUnavailableError(f"Unsupported QWEN_TORCH_DTYPE={torch_dtype}")
    return dtype_map[normalized]


def _parse_model_json(text: str, schema: type[T]) -> T:
    payload = _extract_json_object(text)
    try:
        return schema.model_validate(payload)
    except Exception as exc:
        excerpt = text[:500].replace("\n", " ")
        raise ProviderContractError(f"Qwen response did not match {schema.__name__}: {excerpt}") from exc


def _extract_json_object(text: str) -> Any:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = stripped.strip("`")
        if stripped.lower().startswith("json"):
            stripped = stripped[4:].strip()

    decoder = json.JSONDecoder()
    for index, char in enumerate(stripped):
        if char != "{":
            continue
        try:
            payload, _ = decoder.raw_decode(stripped[index:])
            return payload
        except json.JSONDecodeError:
            continue
    raise ProviderContractError("Qwen response did not include a JSON object")


def _limit_artifact_for_qwen(artifact: UploadedArtifact, max_input_chars: int) -> tuple[UploadedArtifact, list[str]]:
    if len(artifact.text) <= max_input_chars:
        return artifact, []
    excerpt = artifact.text[:max_input_chars]
    omitted = len(artifact.text) - max_input_chars
    return (
        artifact.model_copy(update={"text": excerpt}),
        [f"Qwen input was limited to {max_input_chars} characters; {omitted} characters were omitted for local inference speed."],
    )
