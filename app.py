from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({"message": "Gym Tracker API"})

if __name__ == "__main__":
    app.run(debug=True)