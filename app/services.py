import google.generativeai as genai
from typing import Dict
from app.prompts import *
import datetime as datetime
import json
import os
import uuid
from rapidfuzz import process
from difflib import get_close_matches
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from flask import jsonify
from bson import ObjectId

# Get the absolute path to the app directory
APP_DIR = os.path.dirname(os.path.abspath(__file__))

# Construct the full path to data.json
MOVEMENTS_FILE = os.path.join(APP_DIR, "movements.txt")

model = genai.GenerativeModel(model_name="gemini-1.5-flash")

def load_movements():
    with open(MOVEMENTS_FILE, "r") as file:
        return {line.strip().lower(): line.strip() for line in file}

VALID_MOVEMENTS = load_movements()
PAGE_SIZE = 10

mongo_password = os.getenv("MONGO_DB_PASSWORD")
mongo_username = os.getenv("MONGO_DB_USERNAME")

client = MongoClient(f"mongodb+srv://{mongo_username}:{mongo_password}@cluster0.3qeyv.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0", server_api=ServerApi('1'))
db = client.workout_webapp
collection = db.workout_data

"""
Route Services:
"""

def upload_workout(text: str) -> Dict:

    if detect_workout(text):
        workout_data = format_sms_workout(text)
        upload_to_db(workout_data)
        print("added workout!")

    return {}

def detect_workout(text: str) -> bool:
    print("Detecting workout...")
    prompt=append_to_prompt(text, DETECTION_PROMPT)
    response = model.generate_content([prompt])
    return "True" in response.text

def format_sms_workout(text: str) -> Dict:
    print("Formatting workout...")
    prompt=append_to_prompt(text, FORMATTING_PROMPT)
    response = model.generate_content([prompt])
    workout_data = extract_json(response)
    workout_data['id'] = str(uuid.uuid4())
    workout_data['date'] = datetime.datetime.now().strftime("%Y-%m-%d")
    print('standardizing movements...')
    # standardize movement names:
    workout_data = validate_and_correct_movements(workout_data)

    return workout_data

def extract_json(response):

    # Access the text containing the JSON
    json_text = response.candidates[0].content.parts[0].text

    # Remove Markdown formatting (strip the leading and trailing ```json)
    if json_text.startswith("```json"):
        json_text = json_text[7:]  # Remove the leading ```json
    if json_text.endswith("```\n"):
        json_text = json_text[:-4]  # Remove the trailing ```

    # Parse the JSON string into a Python dictionary
    try:
        return json.loads(json_text)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return {}
    
def get_home_page_wrkts():
    results = collection.find().sort("date", -1).limit(10)
    data = list(results)
    return make_serializable(data)

def aggregate_volume(movement):

    query = {
        "workout": {
            "$elemMatch": {
                "movement": "pull-up"
            }
        }
    }

    results = collection.find(query)
    volume_by_date = {}

    for workout in results:
        for movement_data in workout["workout"]:
            if movement_data["movement"] == movement:
                date = workout["date"]
                volume = sum(set_data["weight"] * set_data["reps"] for set_data in movement_data["sets"])
                volume_by_date[date] = volume

    return volume_by_date

def validate_and_correct_movements(workout_json, valid_movements = VALID_MOVEMENTS):
    for entry in workout_json["workout"]:
        # Normalize the input movement
        movement = entry["movement"].strip().lower()
        
        # Attempt to find a match
        closest_match = get_close_matches(movement, valid_movements, n=1, cutoff=0.6)
        
        if closest_match:
            # Assign the closest valid movement name
            entry["movement"] = closest_match[0]
        else:
            # Assign 'unknown_movement' if no match is found
            entry["movement"] = "unknown_movement"
        
        # Debugging logs
        print(f"Input Movement: {movement}")
        print(f"Closest Match: {closest_match if closest_match else 'No match found'}")
    
    return workout_json

def upload_to_db(workout_data):
    collection.insert_one(workout_data)

def load_movements():
    print(f"Loading movements file from: {MOVEMENTS_FILE}")
    with open(MOVEMENTS_FILE, "r") as file:
        movements = {line.strip().lower(): line.strip() for line in file}
    print(f"Loaded movements: {movements}")
    return movements

def make_serializable(data):
    if isinstance(data, list):
        return [make_serializable(item) for item in data]
    if isinstance(data, dict):
        return {key: make_serializable(value) for key, value in data.items()}
    if isinstance(data, ObjectId):
        return str(data)
    return data