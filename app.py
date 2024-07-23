import io
import pandas as pd
from turtle import pd
from flask import Flask, make_response, render_template, request, redirect, send_file, url_for, flash, session, jsonify
import sqlite3
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import serial
import threading
import time
import base64
import random
import csv
from flask import Response

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed for flash messages and sessions

# Global variable to store the latest RFID tag
latest_rfid_tag = None

# Function to read RFID tags in a separate thread
def read_rfid():
    global latest_rfid_tag
    try:
        ser = serial.Serial('/dev/tty.usbmodem1301', 9600)  # Adjust this to your Arduino port
        while True:
            if ser.in_waiting > 0:
                tag = ser.readline().decode('utf-8').strip()
                latest_rfid_tag = tag
                print(f"Read RFID tag: {tag}")
            time.sleep(1)
    except serial.SerialException as e:
        print(f"SerialException: {e}")
    except Exception as e:
        print(f"Exception: {e}")
    finally:
        if ser and ser.is_open:
            ser.close()
            print("Serial port closed")

# Start the RFID reading thread
rfid_thread = threading.Thread(target=read_rfid, daemon=True)
rfid_thread.start()

# Database setup
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS owner (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            ic_no TEXT NOT NULL,
            dob DATE NOT NULL,
            gender TEXT NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL,
            telephone TEXT NOT NULL,
            address1 TEXT NOT NULL,
            address2 TEXT,
            postal_code TEXT NOT NULL,
            city TEXT NOT NULL,
            district TEXT NOT NULL,
            state TEXT NOT NULL,
            business_type TEXT,
            company_name TEXT,
            registration_no TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS farm (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_id INTEGER NOT NULL,
            premise_id TEXT NOT NULL,
            address1 TEXT NOT NULL,
            address2 TEXT,
            postal_code TEXT NOT NULL,
            city TEXT NOT NULL,
            state TEXT NOT NULL,
            latitude REAL,
            longitude REAL,
            farm_size REAL,
            FOREIGN KEY(owner_id) REFERENCES owner(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS veterinary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            farm_id INTEGER NOT NULL,
            veterinary_name TEXT NOT NULL,
            mobile_number TEXT NOT NULL,
            clinic_name TEXT NOT NULL,
            clinic_number TEXT NOT NULL,
            FOREIGN KEY(farm_id) REFERENCES farm(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS announcements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT NOT NULL,
            date_posted DATE NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS new_entry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rfid TEXT NOT NULL,
            picture BLOB,
            breed_name TEXT NOT NULL,
            gender TEXT NOT NULL,
            dob DATE NOT NULL,
            date_of_entry DATE NOT NULL,
            weight REAL NOT NULL,
            note TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS baby_goat (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rfid TEXT NOT NULL,
            dob DATE NOT NULL,
            gender TEXT NOT NULL,
            father_goat_rfid TEXT,
            mother_goat_rfid TEXT,
            born_weight REAL NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS slaughter (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rfid TEXT NOT NULL,
            gender TEXT NOT NULL,
            dob DATE NOT NULL,
            weight REAL NOT NULL,
            sold_amt REAL,
            buyer_name TEXT,
            cause_of_death TEXT,
            slaughter_cost REAL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS breeding_program (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rfid TEXT NOT NULL,
            partner_id TEXT NOT NULL,
            program_date DATE NOT NULL,
            pregnancy_check_date DATE,
            expected_birth_date DATE,
            breeding_method TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS health (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rfid TEXT NOT NULL,
            clinical_sign TEXT NOT NULL,
            disease_record TEXT NOT NULL,
            medical_record TEXT NOT NULL,
            physical_examination TEXT NOT NULL,
            date_of_vaccination DATE,
            type_of_vaccination TEXT,
            deworming_date DATE,
            type_of_deworming TEXT,
            deticking_date DATE,
            type_of_deticking TEXT,
            notes TEXT,
            officer_name TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT message FROM announcements ORDER BY date_posted DESC')
    announcements = cursor.fetchall()
    conn.close()
    return render_template('index.html', announcements=announcements)


@app.route('/admin_dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if request.method == 'POST':
        announcement = request.form['announcement']
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # Clear previous announcements
        cursor.execute('DELETE FROM announcements')
        
        # Insert the new announcement
        cursor.execute('INSERT INTO announcements (message, date_posted) VALUES (?, ?)', (announcement, datetime.now()))
        conn.commit()
        conn.close()
        return redirect(url_for('admin_dashboard'))
    return render_template('admin_dashboard.html')

@app.route('/about_farm')
def about_farm():
    return render_template('about_farm.html')

@app.route('/price_calculator', methods=['GET', 'POST'])
def price_calculator():
    if request.method == 'POST':
        num_goats = int(request.form['num_goats'])
        feed_per_goat = int(request.form['feed_per_goat'])
        price_per_kg = float(request.form['price_per_kg'])
        total_months = int(request.form['total_months'])

        total_price = ((num_goats * feed_per_goat) / 1000) * price_per_kg * total_months

        return render_template('feed_calculator.html', total_price=total_price)

    return render_template('feed_price_calculator.html', total_price=None)

@app.route('/livestocks', methods=['GET', 'POST'])
def livestocks():
    breed_filter = request.args.get('breed_name')
    gender_filter = request.args.get('gender')
    type_filter = request.args.get('type')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Initialize the query and params
    if type_filter == 'new_born':
        query = 'SELECT rfid, "N/A" as breed_name, dob, gender FROM baby_goat WHERE 1=1'
    else:
        query = 'SELECT rfid, breed_name, dob, gender FROM new_entry WHERE 1=1'
    
    params = []
    if breed_filter and type_filter != 'new_born':
        query += ' AND breed_name = ?'
        params.append(breed_filter)
    if gender_filter:
        query += ' AND gender = ?'
        params.append(gender_filter)
    
    cursor.execute(query, params)
    goats = cursor.fetchall()

    cursor.execute('SELECT DISTINCT breed_name FROM new_entry')
    breed_names = [row[0] for row in cursor.fetchall()]

    conn.close()
    return render_template('livestocks.html', livestocks=goats, breed_names=breed_names, selected_breed=breed_filter, selected_gender=gender_filter, selected_type=type_filter)

@app.route('/export_csv')
def export_csv():
    breed_filter = request.args.get('breed_name')
    gender_filter = request.args.get('gender')
    type_filter = request.args.get('type')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    if type_filter == 'new_born':
        query = 'SELECT rfid, "N/A" as breed_name, dob, gender FROM baby_goat WHERE 1=1'
    else:
        query = 'SELECT rfid, breed_name, dob, gender FROM new_entry WHERE 1=1'
    
    params = []
    if breed_filter and type_filter != 'new_born':
        query += ' AND breed_name = ?'
        params.append(breed_filter)
    if gender_filter:
        query += ' AND gender = ?'
        params.append(gender_filter)

    cursor.execute(query, params)
    rows = cursor.fetchall()

    df = pd.DataFrame(rows, columns=['RFID', 'Breed', 'Date of Birth', 'Gender'])
    
    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)
    
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=livestocks.csv"
    response.headers["Content-type"] = "text/csv"
    return response

    # Convert the data to a DataFrame
    df = pd.DataFrame(goats, columns=['RFID', 'Breed', 'Date of Birth', 'Gender'])

    # Save DataFrame to a CSV buffer
    buffer = io.BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, mimetype='text/csv', download_name='livestocks.csv')

@app.route('/vaccinate')
def vaccinate():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT rfid FROM new_entry')
    goats = cursor.fetchall()

    vaccination_schedule = []
    for goat in goats:
        rfid = goat[0]
        random_days = random.randint(1, 30)
        vaccination_date = (datetime.now() + timedelta(days=random_days)).strftime('%Y-%m-%d')
        vaccination_schedule.append((rfid, vaccination_date))

    return render_template('vaccinate.html', vaccination_schedule=vaccination_schedule)

@app.route('/slaughter_main')
def slaughter_main():
    return render_template('slaughter.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        # Check if admin credentials are used
        if email == 'admin@123.com' and password == 'Admin@123':
            session['user_id'] = 'admin'
            session['is_admin'] = True
            return jsonify({'success': True, 'redirect': url_for('admin_dashboard')})
        else:
            # Connect to the database and check for user credentials
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute('SELECT id, password FROM owner WHERE email = ?', (email,))
            user = cursor.fetchone()
            conn.close()

            if user and check_password_hash(user[1], password):
                session['user_id'] = user[0]
                session['is_admin'] = False
                return jsonify({'success': True, 'redirect': url_for('index')})
            else:
                return jsonify({'success': False, 'message': 'Invalid email or password.'})

    return render_template('login.html')

@app.route('/user_dashboard')
def user_dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    return render_template('user_dashboard.html', user_id=user_id)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

# Baby Goat Registration Routes
@app.route('/baby_goat_registration')
def baby_goat_registration():
    return render_template('baby goat registration_register.html')

@app.route('/baby_goat_registration/register', methods=['GET', 'POST'])
def register_baby_goat():
    if request.method == 'POST':
        rfid = request.form['rfid']
        dob = request.form['dob']
        gender = request.form['gender']
        father_goat_rfid = request.form['father_goat_rfid']
        mother_goat_rfid = request.form['mother_goat_rfid']
        born_weight = request.form['born_weight']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO baby_goat (rfid, dob, gender, father_goat_rfid, mother_goat_rfid, born_weight)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (rfid, dob, gender, father_goat_rfid, mother_goat_rfid, born_weight))
            conn.commit()
            flash('Baby goat registered successfully!', 'success')
            return redirect(url_for('new_goat_actions', rfid=rfid))
        except Exception as e:
            conn.rollback()
            flash(f'Error: {str(e)}', 'danger')
        finally:
            conn.close()

    return render_template('baby goat registration_register.html')

@app.route('/baby_goat_registration/view_certificate/<int:goat_id>')
def view_baby_goat_certificate(goat_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT bg.rfid, bg.dob, bg.gender, bg.father_goat_rfid, bg.mother_goat_rfid, bg.born_weight
        FROM baby_goat bg
        WHERE bg.id = ?
    ''', (goat_id,))
    baby_goat_details = cursor.fetchone()
    conn.close()

    if baby_goat_details:
        return render_template('baby goat registration_certificate.html', details=baby_goat_details)
    else:
        flash('Baby goat not found.', 'danger')
        return redirect(url_for('baby_goat_registration'))

@app.route('/baby_goat_registration/list')
def list_baby_goats():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, dob, gender FROM baby_goat')
    baby_goats = cursor.fetchall()
    conn.close()
    return render_template('baby goat registration_list_baby_goats.html', baby_goats=baby_goats)

@app.route('/baby_goat_registration/search_certificate', methods=['GET', 'POST'])
def search_baby_goat_certificate():
    if request.method == 'POST':
        goat_id = request.form['goat_id']
        return redirect(url_for('view_baby_goat_certificate', goat_id=goat_id))
    return render_template('baby goat registration_search_certificate.html')

# Breeding Program Routes
@app.route('/breeding_program')
def breeding_program():
    rfid = request.args.get('rfid')
    return render_template('breeding program_index2.html', rfid=rfid)

@app.route('/breeding_program/register', methods=['POST'])
def register_breeding_program():
    if request.method == 'POST':
        male_rfid = request.form['male_rfid']
        female_rfid = request.form['female_rfid']
        program_date = request.form['program_date']
        pregnancy_check_date = request.form['pregnancy_check_date']
        expected_birth_date = request.form['expected_birth_date']
        breeding_method = request.form['breeding_method']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO breeding_program (rfid, partner_id, program_date, pregnancy_check_date, expected_birth_date, breeding_method)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (male_rfid, female_rfid, program_date, pregnancy_check_date, expected_birth_date, breeding_method))
            conn.commit()
            flash('Breeding program registered successfully!', 'success')
            return redirect(url_for('new_goat_actions', rfid=male_rfid))
        except Exception as e:
            conn.rollback()
            flash(f'Error: {str(e)}', 'danger')
        finally:
            conn.close()

    return render_template('breeding program_index2.html')

# Existing Goat Registration Routes
@app.route('/existing_goat_registration', methods=['GET', 'POST'])
def existing_goat_registration():
    rfid = request.args.get('rfid') or latest_rfid_tag  # Use latest RFID read or from query param
    if request.method == 'POST':
        rfid = request.form['rfid']
        picture = request.form['image']  # The captured image as a base64 string
        breed = request.form['breed']
        gender = request.form['sex']
        dob = request.form['dob']
        date_of_entry = request.form['dateOfEntry']
        weight = request.form['weight']
        note = request.form['note']

        # Convert the base64 image data to binary
        picture_binary = base64.b64decode(picture.split(',')[1])

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO new_entry (rfid, picture, breed_name, gender, dob, date_of_entry, weight, note)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (rfid, picture_binary, breed, gender, dob, date_of_entry, weight, note))
            conn.commit()
            flash('Goat registered successfully!', 'success')
            return redirect(url_for('existing_goat_registration', rfid=rfid))
        except Exception as e:
            conn.rollback()
            flash(f'Error: {str(e)}', 'danger')
        finally:
            conn.close()

    goat_details = fetch_goat_details(rfid)
    return render_template('existing goat registration_index.html', goat_details=goat_details, rfid=rfid)

@app.route('/authenticate_owner', methods=['POST'])
def authenticate_owner():
    data = request.get_json()
    email = data['email']
    password = data['password']

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, password FROM owner WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user[1], password):
        session['user_id'] = user[0]
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Invalid email or password.'})

def fetch_goat_details(rfid):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT rfid, breed_name, dob, gender, date_of_entry, weight, note FROM new_entry WHERE rfid = ?", (rfid,))
    goat_details = cursor.fetchone()
    conn.close()
    if not goat_details:
        # Return a dictionary with placeholders for all attributes if no goat details are found
        return {'breed_name': '-', 'gender': '-', 'dob': '-', 'date_of_entry': '-', 'weight': '-', 'note': '-'}
    return dict(zip(['rfid', 'breed_name', 'dob', 'gender', 'date_of_entry', 'weight', 'note'], goat_details))

@app.route('/update_goat_details', methods=['POST'])
def update_goat_details():
    rfid = request.form['rfid']
    breed = request.form['breed']
    gender = request.form['gender']
    # Assuming you have more fields to update, retrieve them similarly

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE new_entry SET
            breed_name=?, gender=?
            WHERE rfid=?
        """, (breed, gender, rfid))
        conn.commit()
        flash('Goat details updated successfully!', 'success')
        return redirect(url_for('existing_goat_registration', rfid=rfid))
    except Exception as e:
        conn.rollback()
        flash(f'Error updating goat details: {str(e)}', 'error')
    finally:
        conn.close()
    return redirect(url_for('existing_goat_registration'))

def update_goat_details(rfid, form_data):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE new_entry SET
        breed_name = ?, gender = ?, dob = ?, date_of_entry = ?, weight = ?, note = ?
        WHERE rfid = ?
    """, (form_data['breed'], form_data['gender'], form_data['dob'], form_data['dateOfEntry'],
          form_data['weight'], form_data['note'], rfid))
    conn.commit()
    conn.close()

# Farm Registration Routes
@app.route('/farm_registration')
def farm_registration():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('farm registration_farm.html')

@app.route('/farm_registration/register', methods=['POST'])
def register_farm():
    if 'user_id' not in session:
        flash('Please log in first.', 'danger')
        return redirect(url_for('login'))

    owner_id = session['user_id']
    premise_id = request.form['premise_id']
    address1 = request.form['address1']
    address2 = request.form['address2']
    postal_code = request.form['postal_code']
    city = request.form['city']
    state = request.form['state']
    latitude = request.form['latitude']
    longitude = request.form['longitude']
    farm_size = request.form['farm_size']

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    try:
        # Insert farm data into the farm table
        cursor.execute('''
            INSERT INTO farm (owner_id, premise_id, address1, address2, postal_code, city, state, latitude, longitude, farm_size)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (owner_id, premise_id, address1, address2, postal_code, city, state, latitude, longitude, farm_size))
        farm_id = cursor.lastrowid

        # Insert veterinary details into the veterinary table
        veterinary_names = request.form.getlist('veterinary_name[]')
        mobile_numbers = request.form.getlist('mobile_number[]')
        clinic_names = request.form.getlist('clinic_name[]')
        clinic_numbers = request.form.getlist('clinic_number[]')

        for vet_name, mobile_number, clinic_name, clinic_number in zip(veterinary_names, mobile_numbers, clinic_names, clinic_numbers):
            cursor.execute('''
                INSERT INTO veterinary (farm_id, veterinary_name, mobile_number, clinic_name, clinic_number)
                VALUES (?, ?, ?, ?, ?)
            ''', (farm_id, vet_name, mobile_number, clinic_name, clinic_number))

        conn.commit()
        flash('Farm registered successfully!', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error: {str(e)}', 'danger')
    finally:
        conn.close()

    return redirect(url_for('farm_registration'))

@app.route('/feed_calculator')
def feed_calculator():
    return render_template('feed_calculator.html')

@app.route('/scan')
def scan():
    return render_template('scan.html')

@app.route('/process_scan', methods=['POST'])
def process_scan():
    rfid = request.form['rfid']
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Check in the new_entry table
    cursor.execute('SELECT * FROM new_entry WHERE rfid = ?', (rfid,))
    goat = cursor.fetchone()
    
    # If not found in new_entry, check in baby_goat table
    if not goat:
        cursor.execute('SELECT * FROM baby_goat WHERE rfid = ?', (rfid,))
        goat = cursor.fetchone()
    
    conn.close()

    if goat:
        return redirect(url_for('existing_goat_actions', rfid=rfid))
    else:
        return redirect(url_for('new_goat_actions', rfid=rfid))

@app.route('/read_rfid', methods=['GET'])
def read_rfid():
    global latest_rfid_tag
    if latest_rfid_tag:
        return jsonify({'rfid': latest_rfid_tag})
    return jsonify({'rfid': None})

@app.route('/existing_goat_actions/<rfid>')
def existing_goat_actions(rfid):
    return render_template('existing_goat_actions.html', rfid=rfid)

@app.route('/new_goat_actions/<rfid>')
def new_goat_actions(rfid):
    return render_template('new_goat_actions.html', rfid=rfid)

@app.route('/other_actions/<rfid>')
def other_actions(rfid):
    return render_template('other_actions.html', rfid=rfid)

# Owner Registration Routes
@app.route('/owner_registration')
def owner_registration():
    return render_template('owner registration_index.html')

@app.route('/owner_registration/register', methods=['GET', 'POST'])
def register_owner():
    if request.method == 'POST':
        name = request.form['name']
        ic_no = request.form['ic_no']
        dob = request.form['dob']
        gender = request.form['gender']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        telephone = request.form['telephone']
        address1 = request.form['address1']
        address2 = request.form['address2']
        postal_code = request.form['postal_code']
        city = request.form['city']
        district = request.form['district']
        state = request.form['state']
        business_type = request.form['business_type']
        company_name = request.form['company_name']
        registration_no = request.form['registration_no']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO owner (name, ic_no, dob, gender, email, password, telephone, address1, address2, postal_code, city, district, state, business_type, company_name, registration_no)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, ic_no, dob, gender, email, hashed_password, telephone, address1, address2, postal_code, city, district, state, business_type, company_name, registration_no))
            conn.commit()
            owner_id = cursor.lastrowid
            session['user_id'] = owner_id
            flash('Owner registered successfully!', 'success')
            return redirect(url_for('farm_registration'))
        except Exception as e:
            conn.rollback()
            flash(f'Error: {str(e)}', 'danger')
        finally:
            conn.close()

    return render_template('owner registration_index.html')

# Slaughter Routes
@app.route('/slaughter')
def slaughter():
    return render_template('slaughter_index.html')

@app.route('/register_slaughter', methods=['POST'])
def register_slaughter():
    rfid = request.form.get('rfid')
    gender = request.form.get('gender') if request.form.get('gender') else None
    dob = request.form.get('dob') if request.form.get('dob') else None
    weight = request.form.get('weight') if request.form.get('weight') else None
    sold_amt = request.form.get('sold_amt') if request.form.get('sold_amt') else None
    buyer_name = request.form.get('buyer_name') if request.form.get('buyer_name') else None
    cause_of_death = request.form.get('cause_of_death') if request.form.get('cause_of_death') else None
    slaughter_cost = request.form.get('slaughter_cost') if request.form.get('slaughter_cost') else None

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO slaughter (rfid, gender, dob, weight, sold_amt, buyer_name, cause_of_death, slaughter_cost)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (rfid, gender, dob, weight, sold_amt, buyer_name, cause_of_death, slaughter_cost))
        conn.commit()
        flash('Slaughter registered successfully!', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error: {str(e)}', 'danger')
    finally:
        conn.close()

    return redirect(url_for('slaughter'))

# Health Routes
@app.route('/health')
def health():
    global latest_rfid_tag
    print(f"latest_rfid_tag in health route: {latest_rfid_tag}")  # Debug print
    return render_template('health_index.html', rfid=latest_rfid_tag)

@app.route('/health/register', methods=['GET', 'POST'])
def register_health():
    if request.method == 'POST':
        rfid = request.form['rfid']
        clinical_sign = request.form['clinical_sign']
        disease_record = request.form['disease_record']
        medical_record = request.form['medical_record']
        physical_examination = request.form['physical_examination']
        date_of_vaccination = request.form.get('date_of_vaccination')
        type_of_vaccination = request.form.get('type_of_vaccination')
        deworming_date = request.form.get('deworming_date')
        type_of_deworming = request.form.get('type_of_deworming')
        deticking_date = request.form.get('deticking_date')
        type_of_deticking = request.form.get('type_of_deticking')
        notes = request.form.get('notes')
        officer_name = request.form['officer_name']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO health (rfid, clinical_sign, disease_record, medical_record, physical_examination, date_of_vaccination, type_of_vaccination, deworming_date, type_of_deworming, deticking_date, type_of_deticking, notes, officer_name)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (rfid, clinical_sign, disease_record, medical_record, physical_examination, date_of_vaccination, type_of_vaccination, deworming_date, type_of_deworming, deticking_date, type_of_deticking, notes, officer_name))
            conn.commit()
            flash('Health record registered successfully!', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'Error: {str(e)}', 'danger')
        finally:
            conn.close()

        return redirect(url_for('health'))

    return render_template('health_index.html', rfid=latest_rfid_tag)

@app.route('/view_health_details/<rfid>')
def view_health_details(rfid):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM health WHERE rfid = ?', (rfid,))
    health_record = cursor.fetchone()
    cursor.execute('SELECT * FROM baby_goat WHERE rfid = ?', (rfid,))
    goat_record = cursor.fetchone()
    conn.close()
    
    if health_record and goat_record:
        return render_template('health_details.html', health=health_record, goat=goat_record)
    else:
        flash('No health or goat record found for the scanned RFID', 'danger')
        return redirect(url_for('view_goats'))
    
@app.route('/view_goats')
def view_goats():
    return render_template('scan_health.html')


@app.route('/process_scan_health', methods=['POST'])
def process_scan_health():
    rfid = request.form['rfid']
    return redirect(url_for('view_health_details', rfid=rfid))


@app.route('/get_goat_details', methods=['GET'])
def get_goat_details():
    rfid = request.args.get('rfid')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT gender, dob, weight FROM new_entry WHERE rfid = ?', (rfid,))
    goat_details = cursor.fetchone()
    conn.close()
    if goat_details:
        return jsonify({"success": True, "gender": goat_details[0], "dob": goat_details[1], "weight": goat_details[2]})
    return jsonify({"success": False, "error": "Goat not found"})

# New Route to Display Slaughtered Goats
@app.route('/slaughtered_goats')
def slaughtered_goats():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT rfid, gender, dob, weight, sold_amt, buyer_name, cause_of_death, slaughter_cost FROM slaughter')
    slaughtered_goats = cursor.fetchall()
    conn.close()
    return render_template('slaughtered_goats.html', slaughtered_goats=slaughtered_goats)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
