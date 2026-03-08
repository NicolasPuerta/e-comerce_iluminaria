from backend.db.repository.postgress_repository import PostgressRepository
from backend.db.models.product_model import Product
from backend.db.provider.postgress_provider import PostgresProvider

class ProductRepository(PostgressRepository[Product]):
    def __init__(self, provider: PostgresProvider):
        super().__init__(provider, Product)

    # Aquí puedes agregar métodos específicos para Product si los necesitas
    def get_expensive_products(self, threshold: float):
        with self._provider.get_session_context() as session:
            return session.query(self._model).filter(self._model.price > threshold).all()
