"""
Flask Application for TX Prediction and School Management

This Flask application provides a web API for interacting with a PostgreSQL database and a Keras model.
It supports operations related to school data, term management, ligation orders, user accounts, and predictions based on promoter sequences.

Key Features:
- Connects to a PostgreSQL database for storing and retrieving school-related data and user observations.
- Loads a pre-trained Keras model for making predictions based on promoter sequences.
- Handles CORS to allow cross-origin requests from a specified frontend URL.
- Provides endpoints for adding and querying data related to schools, terms, ligation orders, observations, and user accounts.
- Includes functionality for user sign-up, login, and domain validation.

Endpoints:
- /get_prediction: Returns a prediction based on a promoter sequence.
- /query_schools: Retrieves a list of all schools.
- /query_terms_by_school: Retrieves terms associated with a specific school.
- /insert_observed_TX: Inserts a new observation into the database.
- /query_Observed_TX: Retrieves the average observed TX for a specific sequence.
- /insert_simulated_ligation: Inserts new simulated ligation orders into the database.
- /query_simulated_ligation: Retrieves simulated ligation orders by school and term.
- /handle_signup: Handles user sign-up and account creation.
- /handle_login: Handles user login and authentication.
- /get_valid_domain: Retrieves all valid email domains for sign-up.

Usage:
- Configure the environment variables in a .env file (e.g., MODEL_PATH, DATABASE_URL, FRONTEND_URL).
- Start the Flask server to handle incoming API requests.

Example:
    if __name__ == '__main__':
        populate_schools()
        app.run(host='0.0.0.0', port=port)
"""

from flask import Flask, request, jsonify
from flask_cors import CORS # type: ignore
from keras.saving import load_model # type: ignore
from dotenv import load_dotenv
import os
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine, text

from predict_TX.predict import predict
from database.database import DataBase

# Load environment variables from .env file
load_dotenv()

# Server setup and connection to frontend
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": os.getenv('FRONTEND_URL')}})

# Load model, observed TX database once during startup
model = load_model(os.getenv('MODEL_PATH'))

# Instantiate the Database with the internal PostgreSQL database URL
db = DataBase(os.getenv('DATABASE_URL'))

# Connect to the database engine
engine = create_engine(os.getenv('DATABASE_URL'))

# Function to check and add the 'school_name' column if it doesn't exist
def ensure_school_name_column():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'accounts' AND column_name = 'school_name'
            """))
            columns = [row['column_name'] for row in result]
            if 'school_name' not in columns:
                connection.execute(text("ALTER TABLE accounts ADD COLUMN school_name VARCHAR"))
                print("Column 'school_name' added to 'accounts' table.")
            else:
                print("Column 'school_name' already exists in 'accounts' table.")
    except Exception as e:
        print(f"Error checking or adding column: {str(e)}")

# Populates the schools table in the database with the domains in domains.txt
def populate_schools():
    schools = pd.read_csv('schools.csv')
    for index, row in schools.iterrows():
        db.insert_school(row['name'].strip(), row['domain'].strip())

# Makes prediction based on promoter sequence
@app.route('/get_prediction', methods=['POST'])
def get_prediction():
    try:
        data = request.get_json()    
        prediction = predict(data['codingStrand'], model)
        return jsonify({'prediction': prediction})
    except Exception as e:
        return jsonify({'error': str(e)})

# Queries all schools in the database
@app.route('/query_schools', methods=['POST'])
def query_schools():
    try:
        return jsonify({'schools': db.query_schools()})
    except Exception as e:
        return jsonify({'error': str(e)})
    
# Queries terms by school in the database
@app.route('/query_terms_by_school', methods=['POST'])
def query_terms_by_school():
    try:
        data = request.get_json()  
        return jsonify({'terms': db.query_terms_by_school(data['school'])})
    except Exception as e:
        return jsonify({'error': str(e)})

# Adds new input to the observed TX database
@app.route('/insert_observed_TX', methods=['POST'])
def insert_observed_TX():
    try:
        data = request.get_json()
        success = db.insert_observation(
            data['codingStrand'],
            data['account_email'],
            data['observed_TX'],
            data['students'],
            data['notes'],
            datetime.now().date().strftime('%Y-%m-%d')
        )
        print(f"Observed: {data['observed_TX']}")
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'error': str(e)})

# Queries the observed TX database based on coding strand
@app.route('/query_Observed_TX', methods=['POST'])
def query_Observed_TX():
    try:
        data = request.get_json()
        average_observed_TX = db.query_average_observed_TX_by_sequence(data['codingStrand'])
        return jsonify({'average_observed_TX': average_observed_TX})
    except Exception as e:
        return jsonify({'error': str(e)})

# Adds new student ligation to the database
@app.route('/insert_simulated_ligation', methods=['POST'])
def insert_simulated_ligation():
    try:
        data = request.get_json()
        coding_success = db.insert_ligation_order(
            data['school'],
            data['term'],
            data['orderName'] + '_coding',
            data['sequence'],
            datetime.now().date().strftime('%Y-%m-%d'),
            data['students']
        )
        template_success = db.insert_ligation_order(
            data['school'],
            data['term'],
            data['orderName'] + '_template',
            get_complement(data['sequence']),
            datetime.now().date().strftime('%Y-%m-%d'),
            data['students']
        )
        return jsonify({'success': coding_success and template_success})
    except Exception as e:
        return jsonify({'error': str(e)})

def get_complement(seq):
    mapping = {'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A'}
    return ''.join(mapping[char] for char in seq)

# Queries simulated ligations
@app.route('/query_simulated_ligation', methods=['POST'])
def query_simulated_ligation():
    try:
        data = request.get_json()
        return jsonify({'studentLigations': db.query_ligation_orders_by_school_and_term(data['school'], data['term'])})
    except Exception as e:
        return jsonify({'error': str(e)})

# Handles student sign-up
@app.route('/handle_signup', methods=['POST'])
def handle_signup():
    try:
        data = request.get_json()
        error = db.insert_account(
            data['email'],
            db.query_school_by_domain(data['domain']),
            data['firstName'],
            data['lastName'],
            data['password']
        )
        return jsonify({'error': error})
    except Exception as e:
        return jsonify({'error': str(e)})

# Handles student login
@app.route('/handle_login', methods=['POST'])
def handle_login():
    try:
        data = request.get_json()
        success = db.login_account(data['email'], data['password'])
        first_name, last_name = (db.query_first_name_by_email(data['email']), db.query_last_name_by_email(data['email'])) if success else (None, None)
        return jsonify({'success': success, 'firstName': first_name, 'lastName': last_name})
    except Exception as e:
        return jsonify({'error': str(e)})

# Returns all valid email domains
@app.route('/get_valid_domain', methods=['POST'])
def get_valid_domain():
    try:
        domains = db.query_domains()
        return jsonify({'connection': True, 'domains': domains})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    # Ensure 'school_name' column exists in 'accounts' table
    ensure_school_name_column()
    
    # DO NOT KEEP
    db.delete_all_tables()
    db.reset_table('schools')
    db.reset_table('terms')
    db.reset_table('ligations_orders')
    db.reset_table('accounts')
    db.reset_table('observations')
    # DO NOT KEEP

    populate_schools()
    app.run(host='0.0.0.0', port=1000)
