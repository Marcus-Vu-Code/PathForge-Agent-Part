import os

import pytest

os.environ.setdefault("PATHFORGE_PROVIDER_MODE", "fake")
os.environ.setdefault("PATHFORGE_DATABASE_URL", "sqlite:///./test_pathforge.db")


@pytest.fixture(autouse=True)
def clean_test_db():
    from app.db.database import init_db
    from app.db.tables import StoredProfile, StoredRun
    from app.db.database import SessionLocal

    init_db()
    session = SessionLocal()
    session.query(StoredRun).delete()
    session.query(StoredProfile).delete()
    session.commit()
    session.close()
    yield
