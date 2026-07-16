import os
import shutil

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


def _resolve_db_path() -> str:
    """Return a writable path for the SQLite database.

    Locally the repo file is writable so we use it directly.
    On Streamlit Cloud the repo is read-only; we copy the seed DB to /tmp
    on first run so patient/visit data is available.
    """
    repo_db = os.path.abspath("ckm.db")
    tmp_db  = "/tmp/ckm_app.db"

    # File exists and is writable → local dev, use it directly
    if os.path.exists(repo_db) and os.access(repo_db, os.W_OK):
        return repo_db

    # File doesn't exist yet and the directory is writable → first local run
    if not os.path.exists(repo_db) and os.access(os.path.dirname(repo_db) or ".", os.W_OK):
        return repo_db

    # Read-only filesystem (Streamlit Cloud): copy seed DB to /tmp once
    if not os.path.exists(tmp_db) and os.path.exists(repo_db):
        shutil.copy2(repo_db, tmp_db)
    return tmp_db


DATABASE_URL = f"sqlite:///{_resolve_db_path()}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False, "timeout": 15},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
