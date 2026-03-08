from sqlalchemy import Column, Integer, String, Float
from app.database import Base

class Product(Base):

    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Float)
    description = Column(String)
    image_url = Column(String)