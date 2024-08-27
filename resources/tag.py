from flask_smorest import Blueprint, abort
from flask.views import MethodView
from schemas import TagSchema, TagUpdateSchema, PlainTagSchema, ItemSchema, TagLinkSchema
from models import TagModel, StoreModel, ItemModel
from db import db
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import jwt_required

tag_bp = Blueprint('tag', __name__, description='Operations on tags')


@tag_bp.route('/store/<int:store_id>/tags')
class TagsInStore(MethodView):
    @jwt_required()
    @tag_bp.response(200, TagSchema(many=True))
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)

        return store.tags.all()

    @jwt_required()
    @tag_bp.arguments(PlainTagSchema)
    @tag_bp.response(201, TagSchema)
    def post(self, request_data, store_id):
        if TagModel.query.filter_by(name=request_data['name'], store_id=store_id).first():
            abort(400, message='Tag already exists')

        tag = TagModel(**request_data, store_id=store_id)

        try:
            db.session.add(tag)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message='An error occurred while inserting the tag')

        return tag


@tag_bp.route('/tags/<int:tag_id>')
class Tag(MethodView):
    @jwt_required()
    @tag_bp.response(200, TagSchema)
    def get(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)

        return tag

    @jwt_required()
    @tag_bp.response(204)
    @tag_bp.alt_response(400, description='Tag is linked to an item')
    @tag_bp.alt_response(404, description='Tag not found')
    def delete(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)

        if tag.items:
            abort(400, message='Tag is linked to an item')

        try:
            db.session.delete(tag)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message='An error occurred while deleting the tag')

        return None

    @jwt_required()
    @tag_bp.arguments(TagUpdateSchema)
    @tag_bp.response(200, TagSchema)
    def put(self, request_data, tag_id):
        tag = TagModel.query.get(tag_id)

        if tag is None:
            tag = TagModel(id=tag_id, **request_data)
        else:
            tag.name = request_data['name']

        try:
            db.session.add(tag)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message='An error occurred while updating the tag')

        return tag


@tag_bp.route('/item/<int:item_id>/tag/<int:tag_id>')
class ItemTag(MethodView):
    @jwt_required()
    @tag_bp.arguments(TagLinkSchema)
    @tag_bp.response(201, ItemSchema)
    def post(self, request_data, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        if tag.store_id != request_data['store_id']:
            abort(400, message='Tag does not belong to the store')

        if tag not in item.tags:
            item.tags.append(tag)
        else:
            abort(400, message='Tag already linked to the item')

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message='An error occurred while inserting the tag')

        return item

    @jwt_required()
    @tag_bp.response(200, ItemSchema)
    def delete(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        item.tags.remove(tag)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError as e:
            print(f"Error occured: {e}")
            abort(500, message='An error occurred while deleting the tag')

        return item
