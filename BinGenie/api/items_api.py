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
            return {"message": "Error parsing input", "error": str(e)}, 400

        # Process a new image file if provided.
        file = request.files.get('image')
        if file and file.filename != '':
            # Optionally, delete the old image file if needed.
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            updated_item.image_path = filename

        db.session.commit()
        return schema.dump(updated_item), 200

    def delete(self, id):
        """Delete an item and its associated image file if present."""
        item = Item.query.get_or_404(id)
        image_path = item.image_path
        db.session.delete(item)
        db.session.commit()

        # Attempt to delete the image file if it exists.
        if image_path:
            full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], image_path)
            try:
                if os.path.exists(full_path):
                    os.remove(full_path)
            except OSError as e:
                # Log the error if necessary; here we return a warning message.
                return {"message": "Item deleted but error deleting image", "error": str(e)}, 200

        return {"message": "Item deleted successfully"}, 204


class ItemImageResource(Resource):
    def get(self, item_id):
        """Serve the image file for an item.

        Returns a default image if no image is set.
        """
        directory = current_app.config.get("UPLOAD_FOLDER") or os.environ.get("UPLOAD_FOLDER")
        item = Item.query.get_or_404(item_id)
        if item.image_path:
            image_file = os.path.join(directory, item.image_path)
        else:
            image_file = os.path.join(directory, "default.jpeg")
        if not os.path.isfile(image_file):
            abort(404)
        # Send the file from the directory.
        return send_from_directory(directory, os.path.basename(image_file))


class ItemSearchResource(Resource):
    def get(self):
        """Search for items by name using a query parameter 'q'."""
        query = request.args.get('q')
        if not query:
            return {"message": "No search query provided"}, 400

        search_pattern = f"%{query}%"
        items = Item.query.filter(Item.name.ilike(search_pattern)).all()
        results = []
        for item in items:
            bin_obj = Bin.query.get(item.bin_id)
            location_obj = Location.query.get(bin_obj.location_id) if bin_obj else None
            results.append({
                "item_name": item.name,
                "item_id": str(item.id),
                "bin_id": str(bin_obj.id) if bin_obj else None,
                "bin_name": bin_obj.name if bin_obj else "No Bin",
                "location_id": str(location_obj.id) if location_obj else None,
                "location_name": location_obj.name if location_obj else "No Location"
            })
        return jsonify(results)


# Register resource endpoints.
api.add_resource(ItemsListResource, '/items')
api.add_resource(ItemResource, '/items/<string:id>')
api.add_resource(ItemImageResource, '/item-image/<string:item_id>')
api.add_resource(ItemSearchResource, '/search')
