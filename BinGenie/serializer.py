# schemas.py

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields
from flask import url_for
from .database import db, Location, Bin, Item

class LocationSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Location
        sqla_session = db.session
        load_instance = True
        include_relationships = True
        include_fk = True

    # Optionally, you can include bins in a nested manner:
    bins = fields.List(fields.Nested(lambda: BinSchema(only=("id", "name", "capacity"))))

class BinSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Bin
        sqla_session = db.session
        load_instance = True
        include_relationships = True
        include_fk = True

    # Optionally, include items with limited fields:
    items = fields.List(fields.Nested(lambda: ItemSchema(only=("id", "name", "quantity", "description", "image_url"))))

class ItemSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Item
        sqla_session = db.session
        load_instance = True
        include_relationships = True
        include_fk = True

    # Compute the full image URL using a method field.
    image_url = fields.Method("get_image_url")

    def get_image_url(self, obj):
        if obj.image_path:
            return url_for('static', filename=f"uploads/{obj.image_path}", _external=True)
        return None
