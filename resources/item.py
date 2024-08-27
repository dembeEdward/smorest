from flask_smorest import Blueprint, abort
from flask.views import MethodView
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import jwt_required

from db import db
from models import ItemModel
from schemas import ItemSchema, ItemUpdateSchema

item_bp = Blueprint('item', __name__, description='Item operations')


@item_bp.route('/items')
class ItemList(MethodView):
    @item_bp.response(200, ItemSchema(many=True))
    def get(self):
        return ItemModel.query.all()

    @item_bp.arguments(ItemSchema)
    @item_bp.response(201, ItemSchema)
    def post(self, request_data):
        item = ItemModel(**request_data)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message='Database error')

        return item


@item_bp.route('/items/<int:item_id>')
class Item(MethodView):
    @item_bp.response(200, ItemSchema)
    def get(self, item_id):
        item = ItemModel.query.get_or_404(item_id)

        return item

    @jwt_required()
    @item_bp.arguments(ItemUpdateSchema)
    @item_bp.response(200, ItemSchema)
    def put(self, request_data, item_id):
        item = ItemModel.query.get(item_id)

        if item is None:
            item = ItemModel(id=item_id, **request_data)
        else:
            item['name'] = request_data['name']
            item['price'] = request_data['price']

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message='Database error')

    @jwt_required()
    def delete(self, item_id):
        item = ItemModel.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()

        return None, 204
