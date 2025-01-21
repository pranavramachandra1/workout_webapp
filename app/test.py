import json
from difflib import get_close_matches

# Load valid movements from movements.txt
def load_movements(file_path):
    with open(file_path, "r") as file:
        return [line.strip().lower() for line in file.readlines()]

def validate_and_correct_movements(workout_json, valid_movements):
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

# Example usage
movements_path = "app/movements.txt"
valid_movements = load_movements(movements_path)

# Example generated JSON
generated_json = {
    "workout": [
        {"movement": "Bench prs", "sets": [{"set": 1, "weight": 135, "reps": 10, "failure": False}]},
        {"movement": "DeadLIFT", "sets": [{"set": 1, "weight": 225, "reps": 8, "failure": False}]}
    ]
}

# Validate and correct
corrected_json = validate_and_correct_movements(generated_json, valid_movements)
print(json.dumps(corrected_json, indent=4))
