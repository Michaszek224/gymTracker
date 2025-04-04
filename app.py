from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
from supabase import create_client

# Load environment variables
load_dotenv()

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)

@app.route("/")
def home():
    # API home endpoint
    return jsonify({"message": "Gym Tracker API"})

@app.route("/workouts", methods=["POST"])
def addWorkout():
    # Add a new workout and its exercises
    data = request.json

    response = supabase.table("workout").insert({"day": data["day"]}).execute()

    if not response.data:
        return jsonify({"error": "Failed to add workout"}), 400

    workout_id = response.data[0]["id"]

    exercises = [{
        "workout_id": workout_id,
        "name": ex["name"],
        "reps": ex["reps"],
        "weight": ex["weight"],
        "notes": ex["notes"],
    } for ex in data["exercises"]]

    supabase.table("exercise").insert(exercises).execute()
    
    return jsonify({"message": "Workout added successfully", "workout_id": workout_id})

@app.route("/workouts/<int:workout_id>", methods=["GET"])
def get_workout(workout_id):
    # Retrieve a specific workout and its exercises
    response = supabase.table("workout").select("*").eq("id", workout_id).execute()

    if not response.data:
        return jsonify({"error": "Workout not found"}), 404

    workout = response.data[0]

    exercises_response = supabase.table("exercise").select("*").eq("workout_id", workout_id).execute()
    workout["exercises"] = exercises_response.data

    return jsonify(workout)

@app.route("/workouts", methods=["GET"])
def get_workouts():
    # Retrieve all workouts with their exercises
    response = supabase.table("workout").select("*").execute()

    if not response.data:
        return jsonify({"error": "No workouts found"}), 404

    workouts = {w["id"]: w for w in response.data}

    exercises_response = supabase.table("exercise").select("*").execute()
    if exercises_response.data:
        for ex in exercises_response.data:
            workouts[ex["workout_id"]].setdefault("exercises", []).append(ex)

    return jsonify(workouts)

@app.route("/workouts/<int:workout_id>", methods=["DELETE"])
def delete_workout(workout_id):
    # Delete a workout and its associated exercises
    supabase.table("exercise").delete().eq("workout_id", workout_id).execute()

    response = supabase.table("workout").delete().eq("id", workout_id).execute()

    if response.count == 0:
        return jsonify({"error": "Workout not found"}), 404

    return jsonify({"message": "Workout deleted successfully"})

if __name__ == "__main__":
    # Run the Flask app
    app.run(debug=True)
