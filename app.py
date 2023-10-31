from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

import os

# Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Init db
db = SQLAlchemy(app)

# Init marshmallow
ma = Marshmallow(app)

# Product Class/Model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(200))
    image_url = db.Column(db.String(255))

    def __init__(self, name, description, image_url):
        self.name = name
        self.description = description
        self.image_url = image_url

class ProductSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'description', 'image_url')

# Init schema
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

# Create a product
@app.route('/product', methods=['POST'])
def add_product():
    name = request.json['name']
    description = request.json['description']
    image_url = request.json['image_url']

    new_product = Product(name, description, image_url)

    db.session.add(new_product)
    db.session.commit()

    return product_schema.jsonify(new_product)

# Get all products
@app.route('/product', methods=['GET'])
def get_products():
    all_products = Product.query.all()
    result = products_schema.dump(all_products)
    return jsonify(result)

# Get a single product
@app.route('/product/<id>', methods=['GET'])
def get_product(id):
    product = Product.query.get(id)
    return product_schema.jsonify(product)

# Update a product
@app.route('/product/<id>', methods=['PUT'])
def update_product(id):
    product = Product.query.get(id)

    name = request.json['name']
    description = request.json['description']

    product.name = name
    product.description = description

    db.session.commit()

    return product_schema.jsonify(product)

# Delete a product
@app.route('/product/<id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get(id)
    db.session.delete(product)
    db.session.commit()
    return product_schema.jsonify(product)

# Return image
@app.route('/product/image/<id>', methods=['GET'])
def get_product_image(id):
    product = Product.query.get(id)

    if product is not None and product.image_url is not None:
        image_filename = f"{id}.png"
        image_path = os.path.abspath(os.path.join(basedir, 'images', image_filename))
        if os.path.exists(image_path):
            return send_file(image_path, mimetype='image/jpeg') 

    # If the product or image is not found, return an error message
    return "Image not found", 404


# Run server
if __name__ == '__main__':
    app.run(debug=True)
