import logging

from flask import Blueprint, Response, jsonify, request
from sqlalchemy import insert, select
from werkzeug.security import generate_password_hash

from backend import db
from backend.decorators import timed
from backend.dto.user import UserCreationSchema
from backend.models.user import User, UserSchema
from backend.routes import token_auth

LOGGER = logging.getLogger(__name__)
users_bp = Blueprint("users", __name__, url_prefix="/users")
user_schema = UserSchema()
user_creation_schema = UserCreationSchema()


@timed
@users_bp.route("", methods=["GET"])
@token_auth.login_required  # type: ignore
def get_all_users():
    users = db.session.scalars(select(User)).all()
    return jsonify(user_schema.dump(users, many=True))


@timed
@users_bp.route("", methods=["POST"])
def create_user():
    d = request.json
    new_user = user_creation_schema.load(d)

    db.session.execute(
        insert(User).values(
            username=new_user.username,
            email=new_user.email,
            password=generate_password_hash(new_user.password),
        )
    )
    db.session.commit()
    LOGGER.info(f"Created new user {new_user.username}")
    return Response(status=204)


@timed
@users_bp.route("/<username>")
@token_auth.login_required  # type: ignore
def get_user(username):
    user = db.session.scalars(select(User).where(User.username == username)).one()
    return jsonify(user_schema.dump(user))
