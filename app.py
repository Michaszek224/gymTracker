from flask import Flask, request, render_template, redirect, jsonify
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
    return render_template("index.html")

@app.route("/addWorkout", methods=["GET", "POST"])
def addWorkout():
    if request.method == "POST":
        data = request.form

        # Insert workout into table
        # Check if the day is provided
        response = supabase.table("workout").insert({"day": data["day"]}).execute()
        if not response.data:
            return jsonify({"error": "Failed to add workout"}), 400

        workout_id = response.data[0]["id"]

        names = request.form.getlist('name[]')
        reps = request.form.getlist('reps[]')
        weights = request.form.getlist('weight[]')
        notes = request.form.getlist('notes[]')
    
        exercises = []
        for i in range(len(names)):
            exercises.append({
                'name': names[i],
                'reps': int(reps[i]),
                'weight': float(weights[i]) if weights[i] else None,
                'notes': notes[i]
            })
            
        for exercise in exercises:
            exercise["workout_id"] = workout_id
            response = supabase.table("exercise").insert(exercise).execute()
            if not response.data:
                return jsonify({"error": "Failed to add exercise"}), 400

        return redirect("/workouts")
    return render_template("add_workout.html")

@app.route("/workouts")
def workouts():
    # Fetch all workouts from supabase
    response = supabase.table("workout").select("*").execute()
    workouts = response.data if response.data else []
    return render_template("workouts.html", workouts=workouts)

@app.route("/workouts/<int:workout_id>")
def workout_detail(workout_id):
    # Fetch the specific workout
    response = supabase.table("workout").select("*").eq("id", workout_id).execute()
    workout = response.data[0] if response.data else {}
    exercises_response = supabase.table("exercise").select("*").eq("workout_id", workout_id).execute()
    workout["exercises"] = exercises_response.data
    return render_template("workout_detail.html", workout=workout)

if __name__ == "__main__":
    # Run the Flask app
    app.run(debug=True)
