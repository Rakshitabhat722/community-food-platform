from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

# ---------------- APP CONFIG ----------------
app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'refood.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret_key_for_session'

db = SQLAlchemy(app)

# ---------------- DATABASE MODELS ----------------

class FoodItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    donor_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    food_type = db.Column(db.String(50), nullable=False)
    servings = db.Column(db.Integer, nullable=False)
    tags = db.Column(db.String(200))
    expiry = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='Available')
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)

    def get_image(self):
        if 'veg' in self.food_type.lower():
            return "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=500"
        elif 'bakery' in self.food_type.lower():
            return "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=500"
        else:
            return "https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=500"


class NGO(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    org_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)


# ---------------- CREATE TABLES ----------------
with app.app_context():
    db.create_all()

# ---------------- ROUTES ----------------

# Home page
@app.route('/')
def home():
    items = FoodItem.query.order_by(FoodItem.date_posted.desc()).all()
    return render_template('index.html', items=items)

# Donate food
@app.route('/donate', methods=['GET', 'POST'])
def donate():
    if request.method == 'POST':
        new_food = FoodItem(
            title=request.form['title'],
            description=request.form['description'],
            donor_name=request.form['donor_name'],
            phone=request.form['phone'],
            email=request.form['email'],
            location=request.form['location'],
            food_type=request.form['food_type'],
            servings=request.form['servings'],
            tags=request.form.get('tags'),
            expiry=request.form['expiry']
        )
        db.session.add(new_food)
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('donate.html')

# NGO signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        org_name = request.form['org']
        email = request.form['email']
        password = request.form['password']

        new_ngo = NGO(org_name=org_name, email=email, password=password)
        db.session.add(new_ngo)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('signup.html')

# NGO login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        ngo = NGO.query.filter_by(email=email, password=password).first()

        if ngo:
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error="Invalid credentials")

    return render_template('login.html')

# Reserve food
@app.route('/reserve/<int:id>', methods=['GET', 'POST'])
def reserve(id):
    food = FoodItem.query.get_or_404(id)

    if request.method == 'POST':
        ngo_name = request.form['ngo_name']
        food.status = 'Reserved'
        db.session.commit()

        # Mock email (for demo)
        print("------ EMAIL NOTIFICATION ------")
        print(f"To: {food.email}")
        print(f"Subject: Food Reserved")
        print(f"Message: Your food '{food.title}' has been reserved by {ngo_name}.")
        print("--------------------------------")

        return redirect(url_for('home'))

    return render_template('reserve.html', food=food)


# ---------------- RUN APP ----------------
if __name__ == '__main__':
    app.run(debug=True)
