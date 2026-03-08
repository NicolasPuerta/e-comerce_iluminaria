"""
Implementación del repositorio para PostgreSQL.

Proporciona operaciones CRUD genéricas utilizando SQLAlchemy 
y el proveedor de base de datos.
"""

from typing import List, Optional, Any, Type, TypeVar, Generic
from backend.db.provider.postgress_provider import PostgresProvider

T = TypeVar("T")

class PostgressRepository(Generic[T]):
    """
    Clase base para el repositorio de PostgreSQL utilizando SQLAlchemy.
    """

    def __init__(self, provider: PostgresProvider, model: Type[T]):
        """
        Inicializa el repositorio con un proveedor de base de datos 
        y el modelo correspondiente.
        """
        self._provider = provider
        self._model = model

    def create(self, **kwargs) -> T:
        """Crea un nuevo registro en la base de datos."""
        with self._provider.get_session_context() as session:
            obj = self._model(**kwargs)
            session.add(obj)
            session.flush()  # Asegura que el objeto tenga ID pero no cierra la sesión todavía
            # El commit y refresh ocurren aquí o al final del contexto
            return obj

    def get_all(self) -> List[T]:
        """Obtiene todos los registros del modelo."""
        with self._provider.get_session_context() as session:
            return session.query(self._model).all()

    def get_by_id(self, id: Any) -> Optional[T]:
        """Obtiene un registro por su ID."""
        with self._provider.get_session_context() as session:
            return session.query(self._model).filter(self._model.id == id).first()

    def update(self, id: Any, **kwargs) -> Optional[T]:
        """Actualiza un registro existente."""
        with self._provider.get_session_context() as session:
            obj = session.query(self._model).filter(self._model.id == id).first()
            if obj:
                for key, value in kwargs.items():
                    if hasattr(obj, key):
                        setattr(obj, key, value)
                session.add(obj)
                return obj
            return None

    def delete(self, id: Any) -> bool:
        """Elimina un registro por su ID."""
        with self._provider.get_session_context() as session:
            obj = session.query(self._model).filter(self._model.id == id).first()
            if obj:
                session.delete(obj)
                return True
            return False
