DETECTION_PROMPT= """
You are a detection model. Your task is to determine if a given text is formatted like a workout description. 

A workout description consists of:
1. Movements (e.g., "Bench Press," "Lat Pull Downs").
2. Sets (e.g., "Set 1," "Set 2").
3. Weight (e.g., "135 lbs").
4. Reps (e.g., "10 reps").

### Instructions:
- If the text contains information clearly related to movements, sets, weights, and reps formatted in a structured way that resembles a workout, return **True**.
- If the text does not meet these criteria, return **False**.

### Example Input:
Bench Press:
Set 1: 135 lbs x 10 reps - Failed on last rep
Set 2: 145 lbs x 8 reps
Set 3: 155 lbs x 6 reps
Set 4: 165 lbs x 4 reps
Set 5: 175 lbs x 2 reps

Lat Pull Downs:
Set 1: 100 lbs x 10 reps
Set 2: 110 lbs x 8 reps - Failed on last rep
Set 3: 120 lbs x 6 reps
Set 4: 130 lbs x 4 reps - Failed on last rep
Set 5: 140 lbs x 2 reps

### Expected Output:
True

### Example Input:
Random text with no structure or relevance to a workout.

### Expected Output:
False

### Text to Analyze:# 
# """

FORMATTING_PROMPT = """

You are a formatting model. Your task is to process workout data and format it as a JSON object. The JSON should have the following structure:

{
    "workout": [
        {
            "movement": "<exercise_name>",
            "sets": [
                {
                    "set": <set_number>,
                    "weight": <weight_in_lbs>,
                    "reps": <number_of_reps>,
                    "failure": <true_or_false>
                },
                ...
            ]
        },
        ...
    ]
}

### Example Input:

Bench Press:
Set 1: 135 lbs x 10 reps - Failed on last rep
Set 2: 145 lbs x 8 reps
Set 3: 155 lbs x 6 reps
Set 4: 165 lbs x 4 reps
Set 5: 175 lbs x 2 reps

Lat Pull Downs:
Set 1: 100 lbs x 10 reps
Set 2: 110 lbs x 8 reps - Failed on last rep
Set 3: 120 lbs x 6 reps
Set 4: 130 lbs x 4 reps - Failed on last rep
Set 5: 140 lbs x 2 reps

### Example Output:

{
    "workout": [
        {
            "movement": "Bench Press",
            "sets": [
                { "set": 1, "weight": 135, "reps": 10, "failure": true },
                { "set": 2, "weight": 145, "reps": 8, "failure": false },
                { "set": 3, "weight": 155, "reps": 6, "failure": false },
                { "set": 4, "weight": 165, "reps": 4, "failure": false },
                { "set": 5, "weight": 175, "reps": 2, "failure": false }
            ]
        },
        {
            "movement": "Lat Pull Downs",
            "sets": [
                { "set": 1, "weight": 100, "reps": 10, "failure": false },
                { "set": 2, "weight": 110, "reps": 8, "failure": true },
                { "set": 3, "weight": 120, "reps": 6, "failure": false },
                { "set": 4, "weight": 130, "reps": 4, "failure": true },
                { "set": 5, "weight": 140, "reps": 2, "failure": false }
            ]
        }
    ]
}

Text:
"""

def append_to_prompt(text: str, prompt: str) -> str:
    return prompt + "\n" + text + "\n"