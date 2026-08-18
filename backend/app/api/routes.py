from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.agent.orchestrator import CareerAgent
from app.config import Settings, get_settings
from app.db.database import get_session
from app.models.schemas import (
    ArtifactType,
    BackgroundPromptResponse,
    CareerPlanRequest,
    CareerPlanResponse,
    CareerProfile,
    DocumentSourceSummary,
    ProfileCreateResponse,
    ProviderModeOption,
    ProviderOptionsResponse,
    SelectOption,
    UploadedArtifact,
)
from app.services.document_intake import background_prompt_from_profile, combine_documents, uploaded_file_to_document
from app.services.options import generate_specializations, provider_options
from app.services.run_service import (
    ProfileNotFoundError,
    RunNotFoundError,
    get_profile,
    get_run,
    save_profile,
    save_run,
)


router = APIRouter(prefix="/api")


@router.get("/health")
async def health(settings: Annotated[Settings, Depends(get_settings)]):
    return {"status": "ok", "provider_mode": settings.provider_mode}


@router.get("/provider-options", response_model=ProviderOptionsResponse)
async def get_provider_options(settings: Annotated[Settings, Depends(get_settings)]):
    return provider_options(settings)


@router.get("/goal-specializations", response_model=list[SelectOption])
async def get_goal_specializations(sector: str, target_role: str):
    return generate_specializations(sector, target_role)


@router.post("/profiles/extract")
async def extract_profile(
    background_text: Annotated[str | None, Form()] = None,
    artifact_type: Annotated[ArtifactType, Form()] = ArtifactType.resume,
    provider_mode: Annotated[ProviderModeOption | None, Form()] = None,
    file: UploadFile | None = File(default=None),
    settings: Settings = Depends(get_settings),
):
    text = background_text or ""
    filename = None
    content_type = "text/plain"
    if file is not None:
        filename = file.filename
        content_type = file.content_type or "application/octet-stream"
        document = await uploaded_file_to_document(file, settings.max_upload_bytes)
        text = document.text
    if not text.strip():
        raise HTTPException(status_code=400, detail="Provide background_text or upload a supported document.")
    artifact = UploadedArtifact(artifact_type=artifact_type, filename=filename, content_type=content_type, text=text)
    active_settings = settings.model_copy(update={"provider_mode": provider_mode}) if provider_mode else settings
    extraction = await CareerAgent(active_settings).extract_background(artifact)
    return {"extraction": extraction, "profile": extraction.entities}


@router.post("/background-prompt", response_model=BackgroundPromptResponse)
async def create_background_prompt(
    files: list[UploadFile] | None = File(default=None),
    provider_mode: Annotated[ProviderModeOption | None, Form()] = None,
    settings: Settings = Depends(get_settings),
):
    if not files:
        raise HTTPException(status_code=400, detail="Attach at least one resume, transcript, datasheet, or notes document.")

    documents = [await uploaded_file_to_document(file, settings.max_upload_bytes) for file in files]
    artifact = combine_documents(documents)
    active_settings = settings.model_copy(update={"provider_mode": provider_mode}) if provider_mode else settings
    extraction = await CareerAgent(active_settings).extract_background(artifact)
    prompt = background_prompt_from_profile(extraction, documents)
    sources = [
        DocumentSourceSummary(
            filename=document.filename,
            artifact_type=document.artifact_type,
            content_type=document.content_type,
            character_count=len(document.text),
        )
        for document in documents
    ]
    return BackgroundPromptResponse(
        background_prompt=prompt,
        profile=extraction.entities,
        extraction=extraction,
        sources=sources,
        warnings=extraction.warnings,
    )


@router.post("/profiles", response_model=ProfileCreateResponse)
async def create_profile(profile: CareerProfile, session: Session = Depends(get_session)):
    stored = save_profile(session, profile)
    return ProfileCreateResponse(id=stored.id, profile=profile)


@router.get("/profiles/{profile_id}", response_model=ProfileCreateResponse)
async def read_profile(profile_id: str, session: Session = Depends(get_session)):
    try:
        profile = get_profile(session, profile_id)
    except ProfileNotFoundError:
        raise HTTPException(status_code=404, detail="Profile not found") from None
    return ProfileCreateResponse(id=profile_id, profile=profile)


@router.post("/career-plan", response_model=CareerPlanResponse)
async def create_career_plan(
    request: CareerPlanRequest,
    settings: Settings = Depends(get_settings),
    session: Session = Depends(get_session),
):
    profile = request.profile
    profile_id = request.profile_id
    if profile is None and profile_id:
        try:
            profile = get_profile(session, profile_id)
        except ProfileNotFoundError:
            raise HTTPException(status_code=404, detail="Profile not found") from None
    if profile is None:
        raise HTTPException(status_code=400, detail="Provide profile or profile_id.")
    active_settings = settings.model_copy(update={"provider_mode": request.provider_mode}) if request.provider_mode else settings
    response = await CareerAgent(active_settings).create_plan(profile, request.goal, request.job_description, profile_id)
    save_run(session, response)
    return response


@router.get("/runs/{run_id}", response_model=CareerPlanResponse)
async def read_run(run_id: str, session: Session = Depends(get_session)):
    try:
        return get_run(session, run_id)
    except RunNotFoundError:
        raise HTTPException(status_code=404, detail="Run not found") from None
