from flask import Blueprint, request, jsonify, send_from_directory, render_template, current_app
from flask_cors import CORS
from twilio.twiml.messaging_response import MessagingResponse
import os
from app.services import upload_workout, search_by_uuid, aggregate_volume, get_home_page_wrkts

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

@main.route('/api/get_workout', methods=['GET'])
def get_workout_data():

    id = request.args.get('id', None)

    if not id:
        return jsonify({"error": "No ID provided"}), 400

    try:
        data = search_by_uuid(id)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    if data:
        return jsonify(data), 200

    return jsonify({"error": "Workout not found"}), 404


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