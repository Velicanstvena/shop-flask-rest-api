import os
import requests

from flask.views import MethodView
from flask_smorest import Blueprint, abort
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required, get_jwt
from sqlalchemy import or_
from blocklist import BLOCKLIST
from db import db
from models import UserModel
from schemas import UserSchema, UserRegistrationSchema
from tasks import send_user_registration_email
from flask import current_app

blp = Blueprint('users', __name__, description="Operations on users")

@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserRegistrationSchema)
    def post(self, user_data):
        # check if there is already a user with same username
        if UserModel.query.filter(
            or_(
                UserModel.username == user_data["username"],
                UserModel.email == user_data["email"]
            )
        ).first():
            abort(409, message="User already exists with that username or email.")

        try:
            user = UserModel(
                username = user_data["username"],
                email = user_data["email"],
                password = pbkdf2_sha256.hash(user_data["password"])
            )

            db.session.add(user)
            db.session.commit()

            current_app.queue.enqueue(send_user_registration_email, user.email, user.username)

        except Exception as e:
            abort(400, message=str(e))

        return {"message" : "User created successfully."}, 201

@blp.route("/user/<int:user_id>")
class User(MethodView):
    @blp.response(200, UserSchema)
    def get(self, user_id):
        user = UserModel.query.get_or_404(user_id)

        return user

    def delete(self, user_id):
        user = UserModel.query.get_or_404(user_id)

        db.session.delete(user)
        db.session.commit()

        return {"message" : "User deleted successfully."}, 200

@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        user = UserModel.query.filter(UserModel.username == user_data["username"]).first()

        if user and pbkdf2_sha256.verify(user_data["password"], user.password):
            # jwt is just encoded string, not hashed, we can decode it
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(identity=user.id)

            return {"access_token": access_token, "refresh_token": refresh_token}, 200

        abort(401, message="Invalid credentials")


@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        jti = get_jwt()["jti"] # jwt always has "jti" key, no need to check
        BLOCKLIST.add(jti)

        return {"message": "You have been logged out."}

@blp.route("/refresh")
class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        # Make it clear that when to add the refresh token to the blocklist will depend on the app design
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        return {"access_token": new_token}, 200
