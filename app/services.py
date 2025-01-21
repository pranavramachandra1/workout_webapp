import google.generativeai as genai
from typing import Dict
from app.prompts import *
import datetime as datetime
import json
import os
import uuid
from rapidfuzz import process
from difflib import get_close_matches

# Get the absolute path to the app directory
APP_DIR = os.path.dirname(os.path.abspath(__file__))

# Construct the full path to data.json
DATA_FILE = os.path.join(APP_DIR, "data.json")

model = genai.GenerativeModel(model_name="gemini-1.5-flash")

def load_movements():
    with open("app/movements.txt", "r") as file:
        return {line.strip().lower(): line.strip() for line in file}

VALID_MOVEMENTS = load_movements()
PAGE_SIZE = 10

"""
Route Services:
"""

def upload_workout(text: str) -> Dict:

    if detect_workout(text):
        workout_data = format_sms_workout(text)
        add_workout(workout_data)
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
    breakpoint()
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
    data = read_data()
    if len(data["workouts"]) == 0:
        return []
    if len(data['workouts']) <= PAGE_SIZE:
        return data["workouts"]
    start = (len(data['workouts']) - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    return data["workouts"][start:end]
    
def search_by_uuid(uuid):
    data = read_data()
    for workout in data["workouts"]:
        if workout.get('id', None) and workout['id'] == uuid:
            return workout
    return {}

def aggregate_volume(movement):
    data = read_data()
    volume_by_date = {}

    for workout in data["workouts"]:
        for movement_data in workout["workout"]:
            if movement_data["movement"] == movement:
                date = workout["date"]
                volume = sum(set_data["weight"] * set_data["reps"] for set_data in movement_data["sets"])
                volume_by_date[date] = volume

    return volume_by_date

def read_data():
    with open(DATA_FILE, "r") as file:
        return json.load(file)

def write_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

def add_workout(new_workout):
    data = read_data()  # Load existing data
    data["workouts"].append(new_workout)  # Add the new workout
    write_data(data)  # Save back to the JSON file

# def standardize_movement_name_fuzzy(input_name):
#     input_name = input_name.lower()
#     match, score = process.extractOne(input_name, STANDARD_MOVEMENTS.keys(), score_cutoff=80)
#     return STANDARD_MOVEMENTS[match] if match else input_name

# def standardize_movement_name(input_name):
#     input_name = input_name.lower()
#     for movement in STANDARD_MOVEMENTS:
#         if movement in input_name:
#             return STANDARD_MOVEMENTS[movement]  # Return standardized name
#     return input_name  # Return as-is if no match found

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

# def standardize_workout(workout_data):
#     for movement in workout_data["workout"]:
#         movement["movement"] = standardize_movement_name(movement["movement"])
#     return workout_data

