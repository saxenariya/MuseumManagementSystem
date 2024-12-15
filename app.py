from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql
from datetime import datetime

app = Flask(__name__)
app.secret_key = '1234'

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:vaibhav1234@localhost/Museum'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# User Model
class User(db.Model):
    __tablename__ = 'users'  # Table name in MySQL
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class Plan_to_visit(db.Model):
    __tablename__ = 'plan_to_visits'
    id = db.Column(db.Integer, primary_key=True)
    visitor_name = db.Column(db.String(50), nullable=False)
    visit_date = db.Column(db.Date, nullable=False)
    visit_time = db.Column(db.Time, nullable=False)
    num_tickets = db.Column(db.Integer, nullable=False)
    visitor_type = db.Column(db.String(100),nullable=False)
    price = db.Column(db.Integer, nullable=False)


# Home Route
@app.route('/')
def home():
    return render_template('home.html')


# Register Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']


        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration Successful! Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')


# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and user.password == password:  # Remove check_password_hash and compare directly
            session['user_id'] = user.id
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials. Please try again.')
    return render_template('login.html')


# Dashboard Route
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    visitors = Plan_to_visit.query.all()
    return render_template('dashboard.html', user=user,visitors=visitors)


# Logout Route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))


# Contact Us Route
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        subject = request.form['subject']
        message = request.form['message']

        # Save the contact information to the database (optional)
        # You can create a Contact model if necessary

        flash('Your message has been sent successfully!')
        return redirect(url_for('contact'))
    return render_template('contact.html')


# Plan Your Visit Route
@app.route('/plan-your-visit', methods=['GET', 'POST'])
def plan_your_visit():
    if request.method == 'POST':
        visitor_name = request.form['visitor_name']
        visit_date = request.form['visit_date']
        visit_time = request.form['visit_time']
        num_tickets = request.form['num_tickets']
        visitor_type = request.form['visitor_type']
        price = request.form['price']
        print(visitor_name)

        # Convert visit_time from 12-hour format to 24-hour format using datetime
        try:
            # Parsing the 12-hour format time string and converting to 24-hour format
            visit_time = datetime.strptime(visit_time, '%I:%M %p').time()
        except ValueError:
            flash("Invalid time format. Please use a valid time format (e.g., '10:00 AM').")
            return redirect(url_for('plan_your_visit'))
        # Save the ticket booking information to the database (optional)
        # You can create a Ticket model if necessary
        new_visitor = Plan_to_visit(
            visitor_name=visitor_name,
            visit_date=visit_date,
            visit_time=visit_time,
            num_tickets=num_tickets,
            visitor_type=visitor_type,
            price=price
        )
        print(new_visitor)
        db.session.add(new_visitor)
        db.session.commit()

        flash('Your tickets.css have been booked successfully!')
        return redirect(url_for('booked', visitor_id=new_visitor.id))
    return render_template('plan_your_visit.html')

@app.route('/booked/<int:visitor_id>')
def booked(visitor_id):
    # Fetch the visitor by the passed id
    visitor = Plan_to_visit.query.get(visitor_id)
    
    # If visitor not found, handle the case gracefully
    if not visitor:
        flash("No booking found!")
        return redirect(url_for('plan_your_visit'))

    # Pass the visitor data to the 'booked.html' template
    return render_template('booked.html', visitor=visitor)



# Exhibition Route
@app.route('/exhibition')
def exhibition():
    return render_template('exhibition.html')


# Event Route
@app.route('/event')
def event():
    return render_template('event.html')


@app.route('/forget', methods=['GET', 'POST'])
def forget():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user:

            session['reset_user_id'] = user.id
            return redirect(url_for('reset_password'))
        else:
            flash('No account found with that email.', 'error')
    return render_template('forget_password.html')


@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if 'reset_user_id' not in session:
        flash('Unauthorized access. Please try again.', 'error')
        return redirect(url_for('forget'))

    if request.method == 'POST':
        password = request.form['password']
        user_id = session['reset_user_id']

        user = User.query.get(user_id)
        if user:
            user.password = password
            db.session.commit()

            session.pop('reset_user_id', None)
            flash('Password has been reset successfully!', 'success')
            return redirect(url_for('login'))

    return render_template('reset_password.html')

# Run the App
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure that the database tables are created
    app.run(debug=True)
