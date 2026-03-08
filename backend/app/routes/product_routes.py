from flask import Blueprint, request, jsonify
from app.schemas.product_schema import ProductCreate, ProductResponse
from app.services.product_service import get_products, create_product

product_bp = Blueprint("products", __name__)


@product_bp.route("/products", methods=["GET"])
def list_products():
    pass