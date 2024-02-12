from flask_sqlalchemy import SQLAlchemy
import uuid
from sqlalchemy.dialects.postgresql import UUID

db = SQLAlchemy()

class Location(db.Model):
    __tablename__ = 'locations'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    bins = db.relationship('Bin', backref='location', lazy=True)

class Bin(db.Model):
    __tablename__ = 'bins'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(255), nullable=False)
    capacity = db.Column(db.String(255), nullable=True)
    location_id = db.Column(UUID(as_uuid=True), db.ForeignKey('locations.id'), nullable=False)
    items = db.relationship('Item', backref='bin', lazy=True)

class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    description = db.Column(db.String(255), nullable=True)
    bin_id = db.Column(UUID(as_uuid=True), db.ForeignKey('bins.id'), nullable=False)
    image_path = db.Column(db.String(255), nullable=True)

if __name__ == '__main__':
    db.create_all()
