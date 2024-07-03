from flask import Flask, request, jsonify
from flask_cors import CORS
from keras.saving import load_model

from predict_TX.predict import predict
from observed_TX_db import obs_init
from observed_TX_db import obs_insert
from observed_TX_db import obs_query
from ligate_student_entries.ligate_insert import insert_to_csv

# Server setup and connection to frontend
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3001"}})

# Load model, observed TX database once during startup
model = load_model('predict_TX/model.keras')
obs_init.create_tables()

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

if __name__ == '__main__':
    app.run(debug=True)
