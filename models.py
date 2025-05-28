from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
class Product(db.Model):
    product_id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)

class Location(db.Model):
    location_id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)

class ProductMovement(db.Model):
    movement_id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime)
    from_location = db.Column(db.String, db.ForeignKey('location.location_id'))
    to_location = db.Column(db.String, db.ForeignKey('location.location_id'))
    product_id = db.Column(db.String, db.ForeignKey('product.product_id'))
    qty = db.Column(db.Integer)