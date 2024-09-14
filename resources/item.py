from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt
from sqlalchemy.exc import SQLAlchemyError

from db import db
from models import ItemModel, StoreModel
from schemas import ItemSchema, ItemUpdateSchema

blp = Blueprint('items', __name__, description="Operations on items")

@blp.route("/item/<int:item_id>")
class Item(MethodView):
    @blp.response(200, ItemSchema)
    def get(self, item_id):
        item = ItemModel.query.get_or_404(item_id)
        return item

    @blp.arguments(ItemUpdateSchema)
    @blp.response(200, ItemSchema)
    def put(self, item_data, item_id):
        item = ItemModel.query.get(item_id)

        if item:
            item.name = item_data['name']
            item.price = item_data['price']
        else:
            item = ItemModel(id=item_id, **item_data)

        db.session.add(item)
        db.session.commit()

        return item

    @jwt_required()
    def delete(self, item_id):
        # Usage of claims
        jwt = get_jwt()
        if not jwt.get("is_admin"):
            abort(401, message="Not authorized. Access Denied.")

        item = ItemModel.query.get_or_404(item_id)

        db.session.delete(item)
        db.session.commit()

        return {"message": "Item deleted."}


@blp.route("/item")
class ItemList(MethodView):
    @blp.response(200, ItemSchema(many=True))
    def get(self):
        return ItemModel.query.all()

    @jwt_required(fresh=True)
    @blp.arguments(ItemSchema)
    @blp.response(201, ItemSchema)
    def post(self, item_data):
        item = ItemModel(**item_data)

        # 1. check if the store exists
        store = StoreModel.query.get(item_data["store_id"])
        if store:
            # 2. check if we don't already have the same item in that store
            if ItemModel.query.filter(ItemModel.name == item_data["name"] and store.id == item_data["store_id"]).first():
                abort(404, message="Item already exists")
            else:
                try:
                    db.session.add(item)
                    db.session.commit()
                except SQLAlchemyError:
                    abort(500, message="Database error occurred while inserting the item.")
        else:
            abort(404, message="Store not found.")

        return item
