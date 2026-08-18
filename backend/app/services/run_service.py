from __future__ import annotations

from uuid import uuid4

from sqlalchemy.orm import Session

from app.db.tables import StoredProfile, StoredRun
from app.models.schemas import CareerPlanResponse, CareerProfile


class ProfileNotFoundError(KeyError):
    pass


class RunNotFoundError(KeyError):
    pass


def save_profile(session: Session, profile: CareerProfile) -> StoredProfile:
    stored = StoredProfile(id=str(uuid4()), profile_json=profile.model_dump_json())
    session.add(stored)
    session.commit()
    session.refresh(stored)
    return stored


def get_profile(session: Session, profile_id: str) -> CareerProfile:
    stored = session.get(StoredProfile, profile_id)
    if stored is None:
        raise ProfileNotFoundError(profile_id)
    return CareerProfile.model_validate_json(stored.profile_json)


def save_run(session: Session, response: CareerPlanResponse) -> StoredRun:
    stored = StoredRun(
        id=response.run_id,
        profile_id=response.profile_id,
        response_json=response.model_dump_json(),
    )
    session.add(stored)
    session.commit()
    session.refresh(stored)
    return stored


def get_run(session: Session, run_id: str) -> CareerPlanResponse:
    stored = session.get(StoredRun, run_id)
    if stored is None:
        raise RunNotFoundError(run_id)
    return CareerPlanResponse.model_validate_json(stored.response_json)

