import os
import secrets

from flask import Flask, jsonify
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate, migrate
from sqlalchemy import values

from dotenv import load_dotenv

from db import db
from blocklist import BLOCKLIST
import models

from resources.item import blp as ItemBlueprint
from resources.store import blp as StoreBlueprint
from resources.tag import blp as TagBlueprint
from resources.user import blp as UserBlueprint

def create_app(db_url=None):
    app = Flask(__name__)
    load_dotenv()

    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Stores REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL", "sqlite:///test.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    # flask-migrate is a connection between Alembic and Flask
    migrate = Migrate(app, db)

    api = Api(app)

    # secret key is used for signing the JWTs
    # it is used to verify that our app generated JWT
    # secrets.SystemRandom().getrandbits(128)
    # it should not be stored in code, but in env variable
    app.config["JWT_SECRET_KEY"] = "79518441813193800973500915703908842848"
    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_blocklist(jwt_header, jwt_payload):
        # if this return true that the token has been revoked or no longer available
        return jwt_payload["jti"] in BLOCKLIST

    # this function is called when check_blocklist returns true
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return jsonify({"description": "The token has been revoked.", "error": "token_revoked"}), 401

    # CLAIM = you can add extra information to a JWT other than the subject which is user_id
    # that extra info can be anything we want/need
    @jwt.additional_claims_loader
    def add_claims_to_jwt(identity):
        if identity == 1:
            return {"is_admin": True}
        return {"is_admin": False}

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"message": "The token has expired.", "error": "token_expired"}), 401

    @jwt.invalid_token_loader
    def invalid_token_loader(error):
        return jsonify({"message": "The token is invalid.", "error": "invalid_token"}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({"message": "Missing token.", "error": "authorization_required"}), 401

    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return jsonify({"description": "The token is not fresh.", "error": "fresh_token_required"}, 401)

    # with app.app_context():
    #     db.create_all()

    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(TagBlueprint)
    api.register_blueprint(UserBlueprint)

    return app

# @app.get("/item/<string:item_id>")

# @app.route('/')
# def hello_world():  # put application's code here
#     return 'Hello World!'


# if __name__ == '__main__':
#     app.run()
