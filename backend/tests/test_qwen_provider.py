import pytest

from app.config import Settings
from app.models.schemas import (
    ArtifactType,
    BackgroundArtifactExtraction,
    CareerPlan,
    CareerProfile,
    CareerReasoningRequest,
    RecommendedPath,
    UploadedArtifact,
)
from app.providers.qwen_provider import QwenBackgroundExtractor, QwenCareerReasoner, _resolve_torch_dtype
from tests.fixtures.personas import BACKEND_SWE_TO_ML, ML_GOAL


class FakeQwenClient:
    def __init__(self, text: str):
        self.text = text
        self.calls = []

    def generate(self, messages, max_new_tokens):
        self.calls.append({"messages": messages, "max_new_tokens": max_new_tokens})
        return self.text


@pytest.mark.asyncio
async def test_qwen_reasoner_parses_transformers_json_output():
    plan = CareerPlan(
        recommended_paths=[
            RecommendedPath(
                title="Qwen ML path",
                rationale="Evidence-backed local reasoning",
                fit_summary="Python and backend experience",
                confidence=0.7,
            )
        ],
        overall_confidence=0.7,
    )
    client = FakeQwenClient(f"```json\n{plan.model_dump_json()}\n```")
    settings = Settings(PATHFORGE_PROVIDER_MODE="qwen", QWEN_MAX_NEW_TOKENS=512)
    provider = QwenCareerReasoner(settings, client=client)

    result = await provider.reason(CareerReasoningRequest(profile=BACKEND_SWE_TO_ML, goal=ML_GOAL))

    assert result.provider == "qwen"
    assert result.model_version == "Qwen/Qwen3-4B-Instruct-2507"
    assert result.plan.recommended_paths[0].title == "Qwen ML path"
    assert client.calls[0]["max_new_tokens"] == 512


@pytest.mark.asyncio
async def test_qwen_extractor_limits_large_background_input():
    artifact = UploadedArtifact(
        artifact_type=ArtifactType.resume,
        filename="large-background.txt",
        text="Python AI project. " * 1000,
    )
    extraction = BackgroundArtifactExtraction(
        artifact_id=artifact.artifact_id,
        artifact_type=artifact.artifact_type,
        raw_text="Python AI project.",
        entities=CareerProfile(skills=["Python", "AI"]),
        extraction_confidence=0.7,
    )
    client = FakeQwenClient(extraction.model_dump_json())
    settings = Settings(PATHFORGE_PROVIDER_MODE="qwen", QWEN_MAX_INPUT_CHARS=120)
    provider = QwenBackgroundExtractor(settings, client=client)

    result = await provider.extract(artifact)

    sent_payload = client.calls[0]["messages"][1]["content"]
    assert "Python AI project." in sent_payload
    assert len(sent_payload) < len(artifact.model_dump_json())
    assert any("Qwen input was limited to 120 characters" in warning for warning in result.warnings)


def test_qwen_dtype_setting_resolves_fp16_alias():
    class TorchStub:
        float16 = "float16"
        bfloat16 = "bfloat16"
        float32 = "float32"

    assert _resolve_torch_dtype(TorchStub, "fp16") == "float16"
    assert _resolve_torch_dtype(TorchStub, "auto") == "auto"
