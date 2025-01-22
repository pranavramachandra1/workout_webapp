from pymongo import MongoClient

# Replace <username>, <password>, and <dbname> with your details
uri = "mongodb+srv://pranavramachandra:90fEayRxVH0Jl1iI@cluster0.3qeyv.mongodb.net/workout_app?retryWrites=true&w=majority"


try:
    # Create a client and test connection
    client = MongoClient(uri)
    client.admin.command('ping')
    print("Successfully connected to MongoDB!")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")