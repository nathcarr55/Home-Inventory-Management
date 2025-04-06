# locations_api.py

from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from ..database import Location, db
from ..serializer import LocationSchema

locations_api_bp = Blueprint('locations_api', __name__)
api = Api(locations_api_bp)

class LocationsListResource(Resource):
    def get(self):
        # Retrieve all locations from the database
        locations = Location.query.all()
        schema = LocationSchema(many=True)
        return schema.dump(locations), 200

    def post(self):
        # Create a new location from JSON data
        json_data = request.get_json()
        if not json_data:
            return {'message': 'No input data provided'}, 400

        schema = LocationSchema()
        try:
            # Deserializes input and creates a new Location instance.
            new_location = schema.load(json_data, session=db.session)
        except Exception as e:
            return {'message': 'Error parsing input', 'error': str(e)}, 400

        db.session.add(new_location)
        db.session.commit()
        return schema.dump(new_location), 201

class LocationResource(Resource):
    def get(self, id):
        # Retrieve a single location by id. Note: bins can be included if defined in the serializer.
        location = Location.query.get_or_404(id)
        schema = LocationSchema()
        return schema.dump(location), 200

    def put(self, id):
        # Update an existing location using the provided JSON data.
        location = Location.query.get_or_404(id)
        json_data = request.get_json()
        if not json_data:
            return {'message': 'No input data provided'}, 400

        schema = LocationSchema()
        try:
            # partial=True allows updating only provided fields.
            updated_location = schema.load(json_data, instance=location, partial=True, session=db.session)
        except Exception as e:
            return {'message': 'Error parsing input', 'error': str(e)}, 400

        db.session.commit()
        return schema.dump(updated_location), 200

    def delete(self, id):
        # Delete the specified location
        location = Location.query.get_or_404(id)
        db.session.delete(location)
        db.session.commit()
        return {'message': 'Location deleted successfully'}, 204

# Registering the endpoints:
api.add_resource(LocationsListResource, '/locations')
api.add_resource(LocationResource, '/locations/<string:id>')
