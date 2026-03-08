
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session

from backend.db.provider.base_provider import DataBaseProvider

class PostgresProvider(DataBaseProvider):
    """Factory para crear sesiones de base de datos SQL.

    Example:
        >>> from data_models.db.sql_database_settings import (
        ...     SqlDatabaseSettings
        ... )
        >>> from repositories.user_repository import UserRepository
        >>> settings = SqlDatabaseSettings(
        ...     driver="postgresql",
        ...     user="admin",
        ...     password="password",
        ...     host="localhost",
        ...     port=5432,
        ...     database="mi_base_datos"
        ... )
        >>> provider = PostgresProvider(settings)
        >>> user_repo = UserRepository(provider)
        >>> user_repo.create(
        ...     nombre="Juan",
        ...     email="juan@example.com"
        ... )

    """

    def __init__(self, settings) -> None:
        """Inicializa el proveedor de base de datos SQL.

        Args:
            settings: Configuración de la base de datos SQL

        """
        self._settings = settings
        self._engine: Engine = create_engine(
            self._settings.get_url(),
            pool_size=self._settings.pool_size,
            pool_pre_ping=self._settings.pool_pre_ping,
            pool_recycle=self._settings.pool_recycle,
            echo=self._settings.echo,
        )
        self._session_local: sessionmaker = sessionmaker(
            bind=self._engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )

    @contextmanager
    def get_session_context(self) -> Generator[Session, None, None]:
        """Provee un contexto para una sesión de base de datos SQL.

        Yields:
            Una sesión de base de datos SQL.

        """
        session: Session = self._session_local()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def close(self) -> None:
        """Cierra el engine de la base de datos SQL."""
        self._engine.dispose()
