from os import name

from flask import Flask, render_template, request, jsonify

from database import db
from sqlalchemy import text
import time
from sqlalchemy.exc import OperationalError
from model.client import Client


app = Flask(__name__)

# DATABASE CONFIG
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@db:5432/mydb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
from model.client import Client

# SAME LOGIC FROM TKINTER
programs = {
    "Fat Loss (FL)": {
        "workout": """Mon: Back Squat 5x5 + Core

Tue: EMOM 20min Assault Bike
Wed: Bench Press + 21-15-9
Thu: Deadlift + Box Jumps
Fri: Zone 2 Cardio 30min""",

        "diet": """Breakfast: Egg Whites + Oats
Lunch: Grilled Chicken + Brown Rice
Dinner: Fish Curry + Millet Roti
Target: ~2000 kcal""",

        "color": "#e74c3c",
        "calorie_factor": 22
    },

    "Muscle Gain (MG)": {
        "workout": """Mon: Squat 5x5
Tue: Bench 5x5
Wed: Deadlift 4x6
Thu: Front Squat 4x8
Fri: Incline Press 4x10
Sat: Barbell Rows 4x10""",

        "diet": """Breakfast: Eggs + Peanut Butter Oats
Lunch: Chicken Biryani
Dinner: Mutton Curry + Rice
Target: ~3200 kcal""",

        "color": "#2ecc71",
        "calorie_factor": 35
    },

    "Beginner (BG)": {
        "workout": """Full Body Circuit:
- Air Squats
- Ring Rows
- Push-ups
Focus: Technique & Consistency""",

        "diet": """Balanced Tamil Meals
Idli / Dosa / Rice + Dal
Protein Target: 120g/day""",

        "color": "#3498db",
        "calorie_factor": 26
    }
}


@app.route("/client")
def client_page():
    return render_template("AddClient.html", programs=programs)


@app.route("/program", methods=["POST"])
def program_details():
    try:
        data_req = request.json

        program = data_req.get("program")
        weight = data_req.get("weight")

        if not program:
            return jsonify({"status": "error", "message": "Program required"}), 400

        if weight is None:
            return jsonify({"status": "error", "message": "Weight required"}), 400

        weight = float(weight)

        data = programs.get(program)

        if not data:
            return jsonify({
                "status": "error",
                "message": "Invalid program"
            }), 400

        calorie_factor = data.get("calorie_factor")
        calories = int(weight * calorie_factor)

        return jsonify({
            "workout": data["workout"],
            "diet": data["diet"],
            "color": data["color"],
            "calories": calories
        })

    except Exception as e:
        print("ERROR:", e)
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route("/save_client", methods=["POST"])
def save_client():
   
    name = request.form.get("name")
    age = request.form.get("age")

    height = request.form.get("height")
    weight = request.form.get("weight")

    program = request.form.get("program")

    calories = request.form.get("calories")

    # target_weight = request.form.get("target_weight")
    # target_adherence = request.form.get("target_adherence")

    try:

        client = Client(
            name=name,
            age=age,
            height=height,
            weight=weight,
            program=program,
            calories=calories,
            # target_weight=target_weight,
            # target_adherence=target_adherence
        )
        db.session.add(client)
        db.session.commit()
        return jsonify({
            "status": "success",
            "message": "Client saved successfully"
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })



#----------------------------------dashboard routes-----------------------------------


program = {
    "Fat Loss (FL)": {
        "workout": "Mon: 5x5 Back Squat + AMRAP\nTue: EMOM 20min Assault Bike\nWed: Bench Press + 21-15-9\nThu: 10RFT Deadlifts/Box Jumps\nFri: 30min Active Recovery",
        "diet": "B: 3 Egg Whites + Oats Idli\nL: Grilled Chicken + Brown Rice\nD: Fish Curry + Millet Roti\nTarget: 2,000 kcal",
        "color": "#e74c3c"
    },
    "Muscle Gain (MG)": {
        "workout": "Mon: Squat 5x5\nTue: Bench 5x5\nWed: Deadlift 4x6\nThu: Front Squat 4x8\nFri: Incline Press 4x10\nSat: Barbell Rows 4x10",
        "diet": "B: 4 Eggs + PB Oats\nL: Chicken Biryani\nD: Mutton Curry + Jeera Rice\nTarget: 3,200 kcal",
        "color": "#2ecc71"
    },
    "Beginner (BG)": {
        "workout": "Circuit Training: Air Squats, Ring Rows, Push-ups",
        "diet": "Balanced Tamil Meals: Idli-Sambar, Rice-Dal\nProtein: 120g/day",
        "color": "#3498db"
    }
}

@app.route("/")
def home():
    return render_template("dashboard.html", programs=programs.keys())

@app.route("/program/<name>")
def get_program(name):
    return jsonify(programs[name])

def init_db():
    retries = 10
    while retries > 0:
        try:
            with app.app_context():
                db.create_all()
                print("✅ Tables created successfully")
                return
        except OperationalError as e:
            print(f" DB not ready... retrying ({10 - retries + 1}/10)")
            time.sleep(3)
            retries -= 1

    print(" Could not connect to DB after retries")


if __name__ == "__main__":

