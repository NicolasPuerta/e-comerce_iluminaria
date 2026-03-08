from flask import Flask
from flask_cors import CORS
from app.routes import product_routes

def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:postgres@db:5432/ecommerce"

    CORS(app)

    app.register_blueprint(product_routes)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
