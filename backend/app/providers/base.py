from typing import Protocol

from app.models.schemas import (
    BackgroundArtifactExtraction,
    CareerReasoningRequest,
    CareerReasoningResult,
    UploadedArtifact,
)


class BackgroundExtractor(Protocol):
    async def extract(self, artifact: UploadedArtifact) -> BackgroundArtifactExtraction:
        ...


class CareerReasoner(Protocol):
    async def reason(self, request: CareerReasoningRequest) -> CareerReasoningResult:
        ...


class ProviderContractError(RuntimeError):
    """Raised when an external provider responds with an invalid schema."""


class ProviderUnavailableError(RuntimeError):
    """Raised when a provider is unavailable or times out."""

