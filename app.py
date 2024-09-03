from flask import Flask, request, jsonify
from flask_cors import CORS
from keras.saving import load_model
from dotenv import load_dotenv
import os
from datetime import datetime

from predict_TX.predict import predict
from database.database import Database

# Load environment variables from .env file
load_dotenv()

# Server setup and connection to frontend
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": os.getenv('FRONTEND_URL')}})

# Load model, observed TX database once during startup
model = load_model(os.getenv('MODEL_PATH'))

# Instantiate the Database with the internal PostgreSQL database URL
db = Database(os.getenv('DATABASE_URL'))

# Add CORS headers to all responses.
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', os.getenv('FRONTEND_URL'))
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Populates the schools table in the database with the domains in domains.txt
def populate_schools():
    with open('domains.txt', 'r') as file:
        domains = file.readlines()
    existing_domains = db.query_domains()
    for domain in domains:
        if domain.strip().capitalize() not in existing_domains:
            db.insert_school(domain.strip().capitalize(), domain.strip())

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
        success = db.insert_account(
            data['email'],
            db.query_school_by_domain(data['domain']),
            data['firstName'],
            data['lastName'],
            data['password']
        )
        print(success)
        return jsonify({'success': success})
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
        return jsonify({'domains': domains})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    db = Database(os.getenv('DATABASE_URL'))
    populate_schools()

    port = int(os.environ.get('PORT', 1000))
    app.run(host='0.0.0.0', port=port)
