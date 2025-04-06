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

def populate_schools():
    """
    Populates the schools table and terms table in the database with data from schools_terms.xlsx.

    schools_terms.xlsx has two sheets:
    1. schools: Contains school names and domains.
    2. terms: Contains terms assigned to each school (columns automatically generated based on schools up to column Z).

    Raises:
        ValueError: If a school is present, but has no terms.

    """
    schools_df = pd.read_excel('schools_terms.xlsx', sheet_name='schools')
    terms_df = pd.read_excel('schools_terms.xlsx', sheet_name='terms')
    for index, row in schools_df.iterrows():
        school_name = row['name'].strip()
        school_domain = row['domain'].strip()

        # Check if terms are assigned to school in terms table of schools_terms.xlsx
        if terms_df[school_name].isnull().all():
            raise ValueError(f"Terms for {school_name} are missing.")
        
        # Insert school
        db.insert_school(school_name, school_domain)

        # Insert all terms for the school
        for term_namne in terms_df[school_name]:
            db.insert_term(term_namne, school_name)

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
            data['school'],
            data['term'],
            data['observed_TX'],
            data['students'],
            data['notes'],
            datetime.now().date().strftime('%Y-%m-%d')
        )
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

# Queries for student observations (date, notes, observed TX, sequence, students) based on school and term
@app.route('/query_observations_by_school_and_term', methods=['POST'])
def query_observations_by_school_and_term():
    try:
        data = request.get_json()
        student_observations = db.query_observations_by_school_and_term(data['school'], data['term'])
        return jsonify({'student_observations': student_observations})
    except Exception as e:
        return jsonify({'error': str(e)})

# Gets data for student observations graph based on school and term, preprocessed for frontend
@app.route('/get_student_observations_graph_data', methods=['POST'])
def get_student_observations_graph_data():
    try:
        data = request.get_json()
        student_observations = db.query_observations_by_school_and_term(data['school'], data['term'])
        graph_data = []
        for obs in student_observations:
            graph_data.append({
                'x': predict(obs['Sequence'].upper(), model),
                'y': obs['Observed TX'],
                'label': obs['Sequence']
            })
        return jsonify({
            'label': 'Student Observations',
            'xAxisTitle': 'Predicted Sequence',
            'yAxisTitle': 'Observed TX',
            'data': graph_data
        })
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
            'CGAC' + data['sequence'],
            datetime.now().date().strftime('%Y-%m-%d'),
            data['students']
        )
        template_success = db.insert_ligation_order(
            data['school'],
            data['term'],
            data['orderName'] + '_template',
            'CCGC' + get_reverse_complement(data['sequence']),
            datetime.now().date().strftime('%Y-%m-%d'),
            data['students']
        )
        return jsonify({'success': coding_success and template_success})
    except Exception as e:
        return jsonify({'error': str(e)})

def get_reverse_complement(seq):
    mapping = {'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A'}
    return ''.join(mapping[char] for char in seq)[::-1]

# Queries simulated ligations
@app.route('/query_simulated_ligation', methods=['POST'])
def query_simulated_ligation():
    try:
        data = request.get_json()
        return jsonify(db.query_ligation_orders_by_school_and_term(data['school'], data['term']))
    except Exception as e:
        return jsonify({'error': str(e)})

# Handles student sign-up
@app.route('/handle_signup', methods=['POST'])
def handle_signup():
    try:
        data = request.get_json()
        error = db.insert_account(
            data['email'],
            data['domain'],
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
    populate_schools()
    app.run(host='0.0.0.0', port=1000)
