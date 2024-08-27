from flask_smorest import Blueprint, abort
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from flask_jwt_extended import jwt_required

from db import db
from models import StoreModel
from schemas import StoreSchema

store_bp = Blueprint('store', __name__, description='Store operations')


@store_bp.route('/stores')
class StoreList(MethodView):
    @store_bp.response(200, StoreSchema(many=True))
    def get(self):
        return StoreModel.query.all()

    @jwt_required()
    @store_bp.arguments(StoreSchema)
    @store_bp.response(201, StoreSchema)
    def post(self, request_data):
        store = StoreModel(**request_data)

        try:
            db.session.add(store)
            db.session.commit()
        except IntegrityError:
            abort(400, message='Store already exists')
        except SQLAlchemyError:
            abort(500, message='Database error')

        return store


@store_bp.route('/stores/<int:store_id>')
class Store(MethodView):
    @store_bp.response(200, StoreSchema)
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)

        return store

    @jwt_required()
    def delete(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        db.session.delete(store)
        db.session.commit()

        return None, 204
