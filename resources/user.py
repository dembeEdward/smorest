from flask_smorest import Blueprint, abort
from flask.views import MethodView
from schemas import UserSchema
from models import UserModel, TokenBlockListModel
from passlib.hash import pbkdf2_sha256
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from db import db
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
from datetime import datetime, timezone

user_bp = Blueprint('users', __name__, description='Operations on users')


@user_bp.route('/register')
class RegisterUser(MethodView):
    @user_bp.arguments(UserSchema)
    @user_bp.response(201)
    def post(self, user_data):
        user = UserModel(
            username=user_data['username'],
            password=pbkdf2_sha256.encrypt(user_data['password'])
        )

        try:
            db.session.add(user)
            db.session.commit()

            return {"message": "User has been created successfully"}
        except IntegrityError:
            abort(400, 'Username already exists')
        except SQLAlchemyError:
            abort(500, message='An error occurred while registering user')


@user_bp.route('/login')
class UserLogin(MethodView):
    @user_bp.arguments(UserSchema)
    def post(self, user_data):
        user = UserModel.query.filter_by(
            username=user_data["username"]).first()

        if user and pbkdf2_sha256.verify(user_data['password'], user.password):
            access_token = create_access_token(identity=user.id)
            return {"access_token": access_token}

        return {"message": "Incorrect user credentials"}, 401


@user_bp.route('/logout')
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        jti = get_jwt()['jti']
        now = datetime.now(timezone.utc)
        token = TokenBlockListModel(jti=jti, created_at=now)
        token.save()

        return {"message": "Logout successful"}, 200


@user_bp.route('/users/<int:user_id>')
class UserView(MethodView):
    @jwt_required()
    @user_bp.response(200, UserSchema)
    def get(self, user_id):
        user = UserModel.query.get_or_404(user_id)

        return user

    @jwt_required()
    @user_bp.response(204)
    def delete(self, user_id):
        user = UserModel.query.get_or_404(user_id)

        try:
            db.session.delete(user)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message='An error occurred while deleting user')
