

class PostgresSettings:
    """Gestiona la configuración y parámetros de conexión para PostgreSQL."""

    def __init__(self):
        self.host = os.getenv(DBQscannCredentials.HOST_NAME)
        self.port = os.getenv(DBQscannCredentials.PORT)
        self.username = os.getenv(DBQscannCredentials.USERNAME)
        self.password = os.getenv(DBQscannCredentials.PASSWORD)
        self.database = os.getenv(DBQscannCredentials.SERVICE_NAME)

    def get_url(self):
        """Genera y devuelve la URL de conexión formateada para PostgreSQL.
        Returns:
            str: La URL de conexión completa.
        """
        auth = f"{self.username}:{self.password}"
        server = f"{self.host}:{self.port}"
        return f"postgresql://{auth}@{server}/{self.database}"