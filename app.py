from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
# Fix for database path to avoid location errors
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'refood.db')
app.config['SECRET_KEY'] = 'secret_key_for_session'
db = SQLAlchemy(app)

# --- DATABASE MODEL ---
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
    tags = db.Column(db.String(200), nullable=True)
    status = db.Column(db.String(20), default='Available')
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    
    # --- THIS WAS MISSING BEFORE ---
    expiry = db.Column(db.String(50), nullable=False) 

    def get_image(self):
        if 'Veg' in self.food_type or 'veg' in str(self.tags):
             return "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=500"
        elif 'Bakery' in self.food_type:
             return "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=500"
        else:
             return "https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=500"

# Create DB tables
with app.app_context():
    db.create_all()

# --- ROUTES ---

@app.route('/')
def home():
    items = FoodItem.query.order_by(FoodItem.date_posted.desc()).all()
    return render_template('index.html', items=items)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/ngo-verification')
def ngo_verify():
    return render_template('ngo_verification.html')

@app.route('/donate', methods=['GET', 'POST'])
def donate():
    if request.method == 'POST':
        # Get data from form
        new_food = FoodItem(
            title=request.form['title'],
            description=request.form['description'],
            donor_name=request.form['donor_name'],
            phone=request.form['phone'],
            email=request.form['email'],
            location=request.form['location'],
            food_type=request.form['food_type'],
            servings=request.form['servings'],
            tags=request.form['tags'],
            # This saves the new expiry input
            expiry=request.form['expiry'] 
        )
        db.session.add(new_food)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('donate.html')

@app.route('/reserve/<int:id>', methods=['GET', 'POST'])
def reserve(id):
    food = FoodItem.query.get_or_404(id)
    
    if request.method == 'POST':
        ngo_name = request.form['ngo_name']
        food.status = 'Reserved'
        db.session.commit()
        
        # Mock Email Notification in Terminal
        print(f"--- EMAIL SENT ---")
        print(f"To: {food.email}")
        print(f"Subject: Your food '{food.title}' has been reserved!")
        print(f"Body: Hello {food.donor_name}, the organization '{ngo_name}' is coming to pick up the food.")
        print(f"------------------")
        
        return redirect(url_for('home'))
        
    return render_template('reserve.html', food=food)

if __name__ == '__main__':
    app.run(debug=True)