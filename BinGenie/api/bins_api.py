# bins_api.py

from flask import Blueprint, request, current_app
from flask_restful import Api, Resource
from .database import Bin, Item, db
from .serializer import BinSchema, ItemSchema  # Marshmallow-SQLAlchemy serializers
from werkzeug.utils import secure_filename
import os

bins_api_bp = Blueprint('bins_api', __name__)
api = Api(bins_api_bp)

class BinsListResource(Resource):
    def get(self):
        """List all bins."""
        bins = Bin.query.all()
        schema = BinSchema(many=True)
        return schema.dump(bins), 200

    def post(self):
        """Create a new bin."""
        json_data = request.get_json()
        if not json_data:
            return {"message": "No input data provided"}, 400

        schema = BinSchema()
        try:
            # Deserializes the JSON data into a new Bin instance.
            new_bin = schema.load(json_data, session=db.session)
        except Exception as e:
            return {"message": "Error parsing input", "error": str(e)}, 400

        db.session.add(new_bin)
        db.session.commit()
        return schema.dump(new_bin), 201

class BinResource(Resource):
    def get(self, id):
        """Retrieve details for a single bin (including nested items if configured)."""
        bin_obj = Bin.query.get_or_404(id)
        schema = BinSchema()
        return schema.dump(bin_obj), 200

    def put(self, id):
        """Update an existing bin."""
        bin_obj = Bin.query.get_or_404(id)
        json_data = request.get_json()
        if not json_data:
            return {"message": "No input data provided"}, 400

        schema = BinSchema()
        try:
            # Partial update: only provided fields will be updated.
            updated_bin = schema.load(json_data, instance=bin_obj, partial=True, session=db.session)
        except Exception as e:
            return {"message": "Error parsing input", "error": str(e)}, 400

        db.session.commit()
        return schema.dump(updated_bin), 200

    def delete(self, id):
        """Delete a bin."""
        bin_obj = Bin.query.get_or_404(id)
        db.session.delete(bin_obj)
        db.session.commit()
        return {"message": "Bin deleted successfully"}, 204

class BinItemListResource(Resource):
    def post(self, bin_id):
        """
        Create a new item in a bin.
        Accepts JSON data for non-file fields and optionally a file upload for the image.
        """
        # Ensure the bin exists.
        _ = Bin.query.get_or_404(bin_id)

        # Try to get form data (for file uploads) or JSON.
        data = request.form.to_dict() if request.form else request.get_json()
        if not data:
            return {"message": "No input data provided"}, 400

        # Set the bin_id in the data to associate this item with the bin.
        data['bin_id'] = str(bin_id)
        item_schema = ItemSchema()
        try:
            new_item = item_schema.load(data, session=db.session)
        except Exception as e:
            return {"message": "Error parsing input", "error": str(e)}, 400

        db.session.add(new_item)
        db.session.flush()  # Flush to generate the ID for file naming.

        # Handle file upload if an image file is provided.
        file = request.files.get('image')
        if file:
            file_ext = os.path.splitext(file.filename)[1]
            filename = secure_filename(f"{new_item.id}{file_ext}")
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            # Store only the filename (or relative path) instead of full file path.
            new_item.image_path = filename

        db.session.commit()
        return item_schema.dump(new_item), 201

class BinItemResource(Resource):
    def delete(self, bin_id, item_id):
        """Delete an item from a bin and remove its image if present."""
        # Validate that the bin exists.
        _ = Bin.query.get_or_404(bin_id)
        item = Item.query.get_or_404(item_id)

        db.session.delete(item)
        db.session.commit()

        # Delete the associated image file if it exists.
        if item.image_path:
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], item.image_path)
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except OSError as e:
                return {"message": "Item deleted, but error deleting image", "error": str(e)}, 200

        return {"message": "Item deleted successfully"}, 204

# Register resource endpoints.
api.add_resource(BinsListResource, '/bins')
api.add_resource(BinResource, '/bins/<string:id>')
api.add_resource(BinItemListResource, '/bins/<string:bin_id>/items')
api.add_resource(BinItemResource, '/bins/<string:bin_id>/items/<string:item_id>')
