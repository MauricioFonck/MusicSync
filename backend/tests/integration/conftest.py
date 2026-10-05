from collections.abc import Iterator
from pathlib import Path

import pytest
from sqlalchemy import Engine
from sqlalchemy.orm import Session

from musicsync.infrastructure.database import (
    create_database_engine,
    create_schema,
    create_session_factory,
)


@pytest.fixture
def database_engine(tmp_path: Path) -> Iterator[Engine]:
    engine = create_database_engine(f"sqlite:///{tmp_path / 'musicsync.db'}")
    create_schema(engine)
    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture
def session(database_engine: Engine) -> Iterator[Session]:
    factory = create_session_factory(database_engine)
    db_session = factory()
    try:
        yield db_session
    finally:
        db_session.close()
