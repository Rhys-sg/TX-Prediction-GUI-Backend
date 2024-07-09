from flask import Flask, request, jsonify
from flask_cors import CORS
from keras.saving import load_model
from dotenv import load_dotenv
import os

from predict_TX.predict import predict
from observed_TX_db import obs_init
from observed_TX_db import obs_insert
from observed_TX_db import obs_query
from users_db import users_init
from users_db import users_insert
from users_db import users_query
from ligate_student_entries.ligate_insert import insert_to_csv

# Load environment variables from .env file
load_dotenv()

# Server setup and connection to frontend
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": os.getenv('FRONTEND_URL')}})

# Load model, observed TX database once during startup
model = load_model(os.getenv('MODEL_PATH'))
obs_init.create_tables()
users_init.create_tables()

# Add CORS headers to all responses. Sometimes browsers can be strict with CORS policies. This explicitly sets the CORS headers
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', os.getenv('FRONTEND_URL'))
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Makes prediction based on promoter sequence
@app.route('/get_prediction', methods=['POST'])
def get_prediction():
    try:
        data = request.get_json()    
        prediction = predict(data['codingStrand'], model)
        return jsonify({'prediction': prediction})
    except Exception as e:
        return jsonify({'error': str(e)})


# Adds new input to the observed TX database
@app.route('/insert_observed_TX', methods=['POST'])
def insert_observed_TX():
    try:
        data = request.get_json()    
        input_id = obs_insert.insert_main_data(data['codingStrand'], data['TX'], data['Notes'])
        for student in data['students']:
            obs_insert.insert_student(input_id, student['firstname'], student['lastname'], student['email'])
        return jsonify({'success': 'True'})
    except Exception as e:
        return jsonify({'error': str(e)})
     
 
# Queries the observed TX database based on coding strand, averages the observed TX if there are more than one entry
@app.route('/query_Oberved_TX', methods=['POST'])
def query_Oberved_TX():
    try:
        data = request.get_json()
        entries = obs_query.query_by_coding_strand(data['codingStrand'])
        return jsonify({'entries': entries})
    except Exception as e:
        return jsonify({'error': str(e)})
 
 
# Adds new student ligation (coding and template strand) to the ligation_entries.csv file
@app.route('/insert_simulated_ligation', methods=['POST'])
def insert_simulated_ligation():
    try:
        data = request.get_json()
        insert_to_csv(data, 'ligation_entries.csv')
        return jsonify({'success': 'True'})
    except Exception as e:
        return jsonify({'error': str(e)})

# Handles student sign up and returns if the student has already has account
@app.route('/handle_signup', methods=['POST'])
def handle_signup():
    try:
        data = request.get_json()
        successful = users_insert.register_user(data['fullName'], data['email'], data['password'])
        return jsonify({'successful': successful})
    except Exception as e:
        return jsonify({'error': str(e)})
    

# Handles student login and returns if the student has an account
@app.route('/handle_login', methods=['POST'])
def handle_login():
    try:
        data = request.get_json()
        successful = users_query.login_user(data['email'], data['password'])
        return jsonify({'successful': successful})
    except Exception as e:
        return jsonify({'error': str(e)})
    
    
# returns all valid email domains that are allowed to access GUI (a list in valid_domains.txt)
@app.route('/get_valid_domain', methods=['POST'])
def get_valid_domain():
    try:
        with open('valid_domains.txt', 'r') as file:
            emails = file.readlines()
        return jsonify({'emails': emails})
    except Exception as e:
        return jsonify({'error': str(e)})
        

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 1000))
    app.run(host='0.0.0.0', port=port)