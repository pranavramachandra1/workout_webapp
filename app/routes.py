from flask import Blueprint, request, jsonify, send_from_directory, render_template, current_app
from flask_cors import CORS
import os
from app.services import *

main = Blueprint('main', __name__, static_folder='static', template_folder='templates')
CORS(main)

@main.route('/', endpoint='main')
def serve_index():
    return render_template('main.html')

@main.route('/sms', methods=['GET', 'POST'])
def receive_sms():
    # Get the incoming message
    print(request.form)  # Debug incoming data
    response = request.form
    body = response.get('Body', '')
    upload_workout(body)    
    return "<Response><Message>Message received</Message></Response>", 200

@main.route('/api/get_curr_page', methods=['GET'])
def get_curr_page():

    try:
        data = get_home_page_wrkts()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    if data:
        return jsonify(data), 200

    return jsonify({"error": "Workout not found"}), 404

@main.route('/api/get_volume', methods=['GET'])
def get_volume():

    movement = request.args.get('movement', None)

    if not movement:
        return jsonify({"error": "No movement provided"}), 400

    try:
        data = aggregate_volume(movement)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    if data:
        return jsonify(data), 200
    
    return jsonify({"error": "Movement not found"}), 404

@main.route('/api/get_all_movements', methods=['GET'])
def get_all_movements():

    try:
        with open(os.path.join(current_app.root_path, 'movements.txt'), 'r') as file:
            movements = file.read().splitlines()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(movements), 200

@main.route('/debug-env')
def debug_env():
    import os
    username = os.getenv('MONGO_DB_USERNAME')
    password = os.getenv('MONGO_DB_PASSWORD')
    return f"MONGO_DB_USERNAME: {username}, MONGO_DB_PASSWORD: {password}"

@main.route('/api/last_entry', methods=['GET'])
def last_entry():
    """
    Flask route to fetch the last entered document in the MongoDB collection.
    
    Returns:
        JSON response with the last document or an error message.
    """
    try:
        # Call the get_last function from services.py
        last_document = get_last()
        
        if last_document:
            return jsonify(last_document)
        else:
            return jsonify({"message": "No entries found in the database"}), 404
    except Exception as e:
        print(f"Error in last_entry route: {e}")
        return jsonify({"error": "An error occurred", "details": str(e)}), 500