
import os

from flask import Flask, jsonify
from flask_smorest import Api
from flask_jwt_extended import JWTManager

from resources.item import item_bp
from resources.store import store_bp
from resources.tag import tag_bp
from resources.user import user_bp

from db import db, migrate
import models


def create_app(database_uri=None):
    app = Flask(__name__)
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Store API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = database_uri or os.getenv(
        "DATABASE_URL", "sqlite:///data.db")
    app.config["JWT_SECRET_KEY"] = "1CDA8DAFFCD851352CAC525893133"

    db.init_app(app)
    migrate.init_app(app, db)

    api = Api(app)
    jwt = JWTManager(app)

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify(
                {"message": "Request must contain an access token",
                    "error": "authorization_required"}
            ),
            401
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify(
                {"message": "Token is not valid", "error": "invalid_token"}
            ),
            401
        )

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {"message": "Token has expired", "error": "token_expired"}
            ),
            401
        )

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        token = models.TokenBlockListModel.query.filter_by(jti=jti).first()

        return token is not None

    api.register_blueprint(store_bp)
    api.register_blueprint(item_bp)
    api.register_blueprint(tag_bp)
    api.register_blueprint(user_bp)

    return app
