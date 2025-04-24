from flask import Flask, request, render_template, redirect, jsonify, session, url_for, flash
from dotenv import load_dotenv
import os
from supabase import create_client
from datetime import datetime
from functools import wraps

# Load environment variables
load_dotenv()

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)
# Secret key for signing session cookies
app.secret_key = os.getenv("SECRET_KEY", "super-secret-key")

# Decorator to protect routes
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            flash("Please log in to access this page.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ---------- AUTH ROUTES ----------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            response = supabase.auth.sign_up({
                "email": email,
                "password": password
            })
            user = response.user
            if user:
                # 👇 INSERT user into your own users table
                supabase.table("users").insert({
                    "id": user.id,
                    "username": email
                }).execute()

                flash('Check your email to confirm your account.', 'success')
                return redirect(url_for('login'))
        except Exception as e:
            flash(f'Registration error: {e}', 'danger')
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            auth_response = supabase.auth.sign_in_with_password({"email": email, "password": password})
            user = auth_response.user
            if user:
                session['user_id'] = user.id
                flash('Logged in successfully.', 'success')
                return redirect(url_for('workouts'))
            flash('Invalid credentials.', 'danger')
        except Exception as e:
            flash(f'Login error: {e}', 'danger')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# ---------- PROTECTED APP ROUTES ----------
@app.route("/addWorkout", methods=["GET", "POST"])
@login_required
def addWorkout():
    if request.method == "POST":
        data = request.form
        user_id = session['user_id']
        # Insert workout with user_id
        response = supabase.table("workout").insert({
            "day": data["day"],
            "user_id": user_id
        }).execute()
        if not response.data:
            return jsonify({"error": "Failed to add workout"}), 400

        workout_id = response.data[0]["id"]
        # Collect exercises
        names = request.form.getlist('name[]')
        reps = request.form.getlist('reps[]')
        sets = request.form.getlist('sets[]')
        weights = request.form.getlist('weight[]')
        notes = request.form.getlist('notes[]')

        for i in range(len(names)):
            exercise = {
                'workout_id': workout_id,
                'name': names[i],
                'sets': int(sets[i]),
                'reps': int(reps[i]),
                'weight': float(weights[i]) if weights[i] else None,
                'notes': notes[i]
            }
            resp = supabase.table("exercise").insert(exercise).execute()
            if not resp.data:
                return jsonify({"error": "Failed to add exercise"}), 400

        return redirect(url_for('workouts'))

    today = datetime.today().strftime("%Y-%m-%d")
    return render_template("add_workout.html", default_day=today)

@app.route("/")
@login_required
def workouts():
    # Fetch workouts for this user
    user_id = session['user_id']
    response = supabase.table("workout").select("*").eq("user_id", user_id).execute()
    workouts = response.data or []
    return render_template("workouts.html", workouts=workouts)

@app.route("/exerciseFragment")
@login_required
def exercise_fragment():
    return render_template("exercise_fragment.html")

@app.route("/exerciseFragmentEdit/<int:exercise_id>")
@login_required
def exercise_fragment_edit(exercise_id):
    res = supabase.table("exercise").select("*").eq("id", exercise_id).execute()
    if not res.data:
        return "Exercise not found", 404
    exercise = res.data[0]
    return render_template("exercise_fragment_edit.html", exercise=exercise)

@app.route("/updateExercise/<int:exercise_id>", methods=["POST"])
@login_required
def updateExercise(exercise_id):
    data = request.form
    exercise = {
        "name": data["name"],
        "sets": int(data["sets"]),
        "reps": int(data["reps"]),
        "weight": float(data["weight"]) if data["weight"] else None,
        "notes": data["notes"]
    }
    res = supabase.table("exercise").update(exercise).eq("id", exercise_id).execute()
    if not res.data:
        return jsonify({"error": "Failed to update exercise"}), 400
    updated = res.data[0]
    return render_template("exercise_display_fragment.html", exercise=updated)

@app.route("/workouts/<int:workout_id>")
@login_required
def workout_detail(workout_id):
    w = supabase.table("workout").select("*").eq("id", workout_id).execute()
    workout = w.data[0] if w.data else {}
    ex = supabase.table("exercise").select("*").eq("workout_id", workout_id).execute()
    workout["exercises"] = ex.data
    return render_template("workout_detail.html", workout=workout)

@app.route("/deleteWorkout/<int:workout_id>", methods=["DELETE"])
@login_required
def deleteWorkout(workout_id):
    supabase.table("exercise").delete().eq("workout_id", workout_id).execute()
    supabase.table("workout").delete().eq("id", workout_id).execute()
    return "", 200

@app.route("/deleteExercise/<int:exercise_id>", methods=["DELETE"])
@login_required
def deleteExercise(exercise_id):
    supabase.table("exercise").delete().eq("id", exercise_id).execute()
    return "", 200

@app.route("/updateWorkout/<int:workout_id>/addExercises", methods=["POST"])
@login_required
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
        resp = supabase.table("exercise").insert(exercise).execute()
        if not resp.data:
            return jsonify({"error": "Failed to add exercise"}), 400

    return redirect(url_for('workout_detail', workout_id=workout_id))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
