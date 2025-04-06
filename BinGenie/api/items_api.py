# items_api.py

from flask import Blueprint, request, current_app, jsonify, abort, send_from_directory
from flask_restful import Api, Resource
from .database import Item, Bin, Location, db
from .serializer import ItemSchema
from werkzeug.utils import secure_filename
import os

items_api_bp = Blueprint('items_api', __name__)
api = Api(items_api_bp)


class ItemsListResource(Resource):
    def get(self):
        """List all items."""
        items = Item.query.all()
        schema = ItemSchema(many=True)
        return schema.dump(items), 200

    def post(self):
        """Create a new item.

        Accepts JSON or form data. For file uploads, include an 'image' file in the request.
        """
        # Support both form data (for file uploads) and JSON data.
        data = request.form.to_dict() if request.form else request.get_json()
        if not data:
            return {"message": "No input data provided"}, 400

        # Ensure the bin_id is provided correctly.
        data['bin_id'] = data.get('bin_id')
        schema = ItemSchema()
        try:
            # Deserialize into an Item instance.
            new_item = schema.load(data, session=db.session)
        except Exception as e:
            return {"message": "Error parsing input", "error": str(e)}, 400

        db.session.add(new_item)
        db.session.flush()  # Flush to generate new_item.id for file naming.

        # Process file upload if an image is provided.
        file = request.files.get('image')
        if file:
            file_ext = os.path.splitext(file.filename)[1]
            filename = secure_filename(f"{new_item.id}{file_ext}")
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            # Save just the filename for later retrieval.
            new_item.image_path = filename

        db.session.commit()
        return schema.dump(new_item), 201


class ItemResource(Resource):
    def get(self, id):
        """Retrieve a single item by id."""
        item = Item.query.get_or_404(id)
        schema = ItemSchema()
        return schema.dump(item), 200

    def put(self, id):
        """Update an existing item.

        Accepts partial updates in JSON or form data. Processes file upload if a new image is provided.
        """
        item = Item.query.get_or_404(id)
        data = request.form.to_dict() if request.form else request.get_json()
        if not data:
            return {"message": "No input data provided"}, 400

        schema = ItemSchema()
        try:
            # Use partial=True so only provided fields are updated.
            updated_item = schema.load(data, instance=item, partial=True, session=db.session)
        except Exception as e:
            return {"message": "Error parsing input", "error": str(e
