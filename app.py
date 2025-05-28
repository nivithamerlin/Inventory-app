from flask import Flask, render_template, request, redirect, url_for
from models import db, Product, Location, ProductMovement
from datetime import datetime
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret'
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return redirect('/products')


@app.route('/products', methods=['GET', 'POST'])
def products():
    if request.method == 'POST':
        product_id = request.form['product_id']
        name = request.form['name']
        if product_id and name:
            db.session.add(Product(product_id=product_id, name=name))
            db.session.commit()
        return redirect('/products')
    all_products = Product.query.all()
    return render_template('product.html', products=all_products)

# Edit Product
@app.route('/product/edit/<product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    if request.method == 'POST':
        product.name = request.form['name']
        db.session.commit()
        return redirect('/products')
    return render_template('edit_product.html', product=product)

# Delete Product
@app.route('/product/delete/<product_id>')
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return redirect('/products')



#location part
@app.route('/locations', methods=['GET', 'POST'])
def locations():
    if request.method == 'POST':
        location_id = request.form['location_id']
        name = request.form['name']
        if location_id and name:
            db.session.add(Location(location_id=location_id, name=name))
            db.session.commit()
        return redirect('/locations')

    all_locations = Location.query.all()
    return render_template('location.html', locations=all_locations)

@app.route('/location/edit/<location_id>', methods=['GET', 'POST'])
def edit_location(location_id):
    location = Location.query.get_or_404(location_id)
    if request.method == 'POST':
        location.name = request.form['name']
        db.session.commit()
        return redirect('/locations')
    return render_template('edit_location.html', location=location)

@app.route('/location/delete/<location_id>')
def delete_location(location_id):
    location = Location.query.get_or_404(location_id)
    db.session.delete(location)
    db.session.commit()
    return redirect('/locations')

#product_movement

@app.route('/movements', methods=['GET', 'POST'])
def movements():
    products = Product.query.all()
    locations = Location.query.all()

    if request.method == 'POST':
        product_id = request.form['product_id']
        from_location = request.form.get('from_location') or None
        to_location = request.form.get('to_location') or None
        qty = int(request.form['qty'])


        movement = ProductMovement(
            timestamp=datetime.now(),
            product_id=product_id,
            from_location=from_location,
            to_location=to_location,
            qty=qty
        )
        db.session.add(movement)
        db.session.commit()
        return redirect('/movements')

    all_movements = ProductMovement.query.order_by(ProductMovement.timestamp.desc()).all()
    return render_template('movement.html', movements=all_movements, products=products, locations=locations)

#Report module

from collections import defaultdict

@app.route('/report')
def report():
    # Query all movements
    movements = ProductMovement.query.all()

    # Dictionary to track stock per (product_id, location_id)
    stock = defaultdict(int)

    for m in movements:
        key_from = (m.product_id, m.from_location)
        key_to = (m.product_id, m.to_location)

        # If moving OUT from a location, subtract qty
        if m.from_location:
            stock[key_from] -= m.qty

        # If moving IN to a location, add qty
        if m.to_location:
            stock[key_to] += m.qty

    # Convert to list of dicts for rendering
    report_data = []
    for (product_id, location_id), qty in stock.items():
        if location_id:  # skip movements with no destination
            report_data.append({
                'product_id': product_id,
                'location_id': location_id,
                'qty': qty
            })

    return render_template('report.html', report=report_data)

if __name__ == '__main__':
    print("Flask is starting...")
    app.run(debug=True)