from flask import Flask, request, render_template, redirect, jsonify
from dotenv import load_dotenv
import os
from supabase import create_client
from datetime import datetime

# Load environment variables
load_dotenv()

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)

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
        sets = request.form.getlist('sets[]')
        weights = request.form.getlist('weight[]')
        notes = request.form.getlist('notes[]')
    
        exercises = []
        for i in range(len(names)):
            exercises.append({
                'name': names[i],
                'sets': int(sets[i]),
                'reps': int(reps[i]),
                'weight': float(weights[i]) if weights[i] else None,
                'notes': notes[i]
            })
            
        for exercise in exercises:
            exercise["workout_id"] = workout_id
            response = supabase.table("exercise").insert(exercise).execute()
            if not response.data:
                return jsonify({"error": "Failed to add exercise"}), 400

        return redirect("/")
    today = datetime.today().strftime("%Y-%m-%d")
    return render_template("add_workout.html", default_day=today)

@app.route("/")
def workouts():
    # Fetch all workouts from supabase
    response = supabase.table("workout").select("*").execute()
    workouts = response.data if response.data else []
    return render_template("workouts.html", workouts=workouts)

@app.route("/exerciseFragment")
def exercise_fragment():
    # Render the exercise fragment template
    return render_template("exercise_fragment.html")

@app.route("/workouts/<int:workout_id>")
def workout_detail(workout_id):
    # Fetch the specific workout
    response = supabase.table("workout").select("*").eq("id", workout_id).execute()
    workout = response.data[0] if response.data else {}
    exercises_response = supabase.table("exercise").select("*").eq("workout_id", workout_id).execute()
    workout["exercises"] = exercises_response.data
    return render_template("workout_detail.html", workout=workout)

@app.route("/deleteWorkout/<int:workout_id>", methods=["DELETE"])
def deleteWorkout(workout_id):
    # Delete the workout and its exercises
    supabase.table("exercise").delete().eq("workout_id", workout_id).execute()
    supabase.table("workout").delete().eq("id", workout_id).execute()
    print(f"Deleting workout {workout_id}")
    return "", 200

@app.route("/deleteExercise/<int:exercise_id>", methods=["DELETE"])
def deleteExercise(exercise_id):
    # Delete the exercise
    supabase.table("exercise").delete().eq("id", exercise_id).execute()
    print(f"Deleting exercise {exercise_id}")
    return "", 200

@app.route("/updateWorkout/<int:workout_id>/addExercises", methods=["POST"])
def updateWorkoutAddExercises(workout_id):
    names = request.form.getlist('name[]')
    reps = request.form.getlist('reps[]')
    sets = request.form.getlist('sets[]')
    weights = request.form.getlist('weight[]')
    notes = request.form.getlist('notes[]')
    
    for i in range(len(names)):
        exercise = {
            "workout_id": workout_id,
            "name": names[i],
            "sets": int(sets[i]),
            "reps": int(reps[i]),
            "weight": float(weights[i]) if weights[i] else None,
            "notes": notes[i]
        }
        response = supabase.table("exercise").insert(exercise).execute()
        if not response.data:
            return jsonify({"error": "Failed to add exercise"}), 400
    
    return redirect("/workouts/" + str(workout_id))


if __name__ == "__main__":
    # Run the Flask app
    port = int(os.environ.get("PORT", 5000))  # Use the Render-provided port or default to 5000
    app.run(host='0.0.0.0', port=port)