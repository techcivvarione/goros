"""Database primitives shared across the application."""

from __future__ import annotations

from collections.abc import Generator, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field

from sqlalchemy import MetaData, create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import Settings

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""

    metadata = MetaData(naming_convention=NAMING_CONVENTION)


@dataclass(slots=True)
class DatabaseManager:
    """Owns the SQLAlchemy engine and session factory for the process."""

    settings: Settings
    engine: Engine | None = None
    session_factory: sessionmaker[Session] | None = None
    _initialized: bool = field(default=False, init=False, repr=False)

    def initialize(self) -> None:
        """Initialize the SQLAlchemy engine and session factory."""

        if self._initialized:
            return

        connect_args: dict[str, object] = {}
        if self.settings.database_url.startswith("sqlite"):
            connect_args["check_same_thread"] = False

        self.engine = create_engine(
            self.settings.database_url,
            echo=self.settings.database_echo,
            pool_pre_ping=True,
            connect_args=connect_args,
        )
        self.session_factory = sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )
        self._initialized = True

    def dispose(self) -> None:
        """Dispose the SQLAlchemy engine and reset the manager."""

        if self.engine is not None:
            self.engine.dispose()
        self.engine = None
        self.session_factory = None
        self._initialized = False

    @property
    def is_initialized(self) -> bool:
        """Return whether the database manager has been initialized."""

        return (
            self._initialized
            and self.engine is not None
            and self.session_factory is not None
        )

    @contextmanager
    def session(self) -> Iterator[Session]:
        """Open a database session scoped to a single request or operation."""

        if self.session_factory is None:
            raise RuntimeError("DatabaseManager has not been initialized.")

        session = self.session_factory()
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def healthcheck(self) -> bool:
        """Validate that the database is reachable."""

        if self.engine is None:
            return False

        with self.engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True


def create_database_manager(settings: Settings) -> DatabaseManager:
    """Build a database manager from application settings."""

    return DatabaseManager(settings=settings)


def get_db_session(manager: DatabaseManager) -> Generator[Session, None, None]:
    """Yield a database session from an initialized manager."""

    with manager.session() as session:
        yield session
