"""Módulo que provee la clase base abstracta para proveedores de base de datos."""

from abc import ABC, abstractmethod
from typing import Generator


class DataBaseProvider(ABC):
    """Clase base abstracta para proveedores de base de datos.

    Example:
        >>> # Crear un proveedor (En este caso PostgresProvider es una implementación
        >>> # de DataBaseProvider)
        >>> provider = PostgresProvider(settings)
            ...
        >>> # Usar el contexto de sesión
        >>> with provider.get_session_context() as session:
                # Realizar operaciones con la base de datos
                result = session.query(Model).all()
            ...
        >>> # Cerrar la conexión cuando ya no se necesite
        >>> provider.close()

    """

    @abstractmethod
    def get_session_context(self) -> Generator:
        """Provee un contexto para una sesión de base de datos.

        Yields:
            Una sesión de base de datos.

        """
        ...

    @abstractmethod
    def close(self) -> None:
        """Cierra la conexión de la base de datos."""