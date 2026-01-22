import sqlite3
import os
import random
import bcrypt
import requests
from functools import wraps
from datetime import datetime
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session,
    flash,
    Response
)

# -----------------------------
# App Setup
# -----------------------------
app = Flask(__name__)
app.secret_key = "gym_super_secret"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "database.db")

# -----------------------------
# Import gym logic
# -----------------------------
from utils.calculations import (
    calculate_bmi,
    bmi_category,
    daily_calories,
    daily_protein
)
from utils.workouts import get_today_workout
from utils.emailer import send_login_alert, send_otp


# -----------------------------
# DATABASE INIT
# -----------------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            mobile TEXT,
            password TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS login_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            login_time TEXT,
            ip_address TEXT,
            location TEXT
        )
    """)

    conn.commit()
    conn.close()


# -----------------------------
# HELPER: LOCATION
# -----------------------------
def get_location(ip):
    try:
        res = requests.get(
            f"https://ipapi.co/{ip}/json/",
            timeout=3
        ).json()
        city = res.get("city", "")
        country = res.get("country_name", "")
        return f"{city}, {country}".strip(", ")
    except:
        return "Unknown"
    
def login_required(route_function):
    @wraps(route_function)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/")
        return route_function(*args, **kwargs)
    return wrapper


# -----------------------------
# LOGIN PAGE
# -----------------------------
@app.route("/")
def home():
    return render_template("login.html")


# -----------------------------
# LOGIN
# -----------------------------
@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]

    conn = sqlite3.connect(DB_PATH, timeout=10)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, name, email, mobile, password FROM users WHERE email=?",
        (email,)
    )
    user = cursor.fetchone()

    if not user:
        conn.close()
        return render_template("login.html", error="Account not found")

    if not bcrypt.checkpw(password.encode(), user[4].encode()):
        conn.close()
        return render_template("login.html", error="Wrong password")
        session["user_id"] = user[0]
        session["user_name"] = user[1]

    # Save login history
    ip = request.remote_addr or "0.0.0.0"
    location = get_location(ip)
    login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO login_logs (user_id, login_time, ip_address, location)
        VALUES (?, ?, ?, ?)
    """, (user[0], login_time, ip, location))

    conn.commit()
    conn.close()

    return render_template(
        "health_form.html",
        name=user[1],
        email=user[2],
        mobile=user[3]
    )



# -----------------------------
# REGISTER
# -----------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        mobile = request.form["mobile"]
        password = request.form["password"]

        hashed = bcrypt.hashpw(
            password.encode(),
            bcrypt.gensalt()
        ).decode()

        conn = sqlite3.connect(DB_PATH, timeout=10)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id FROM users WHERE email=?",
            (email,)
        )
        if cursor.fetchone():
            conn.close()
            return render_template(
                "register.html",
                error="Email already exists"
            )

        cursor.execute("""
            INSERT INTO users (name, email, mobile, password)
            VALUES (?, ?, ?, ?)
        """, (name, email, mobile, hashed))

        conn.commit()
        conn.close()

        # Email alert (non-blocking)
        try:
            send_login_alert(name, email)
        except Exception as e:
            print("Email alert failed:", e)

        flash("Account created successfully. Please login.", "success")
        return redirect("/")

    return render_template("register.html")


# -----------------------------
# FORGOT PASSWORD
# -----------------------------
@app.route("/forgot", methods=["GET", "POST"])
def forgot():
    if request.method == "POST":
        email = request.form["email"]

        conn = sqlite3.connect(DB_PATH, timeout=10)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM users WHERE email=?",
            (email,)
        )
        user = cursor.fetchone()
        conn.close()

        if not user:
            return render_template(
                "forgot.html",
                error="Email not found"
            )

        otp = str(random.randint(100000, 999999))
        session["reset_otp"] = otp
        session["reset_email"] = email

        send_otp(email, otp)
        return redirect("/verify-otp")

    return render_template("forgot.html")


# -----------------------------
# VERIFY OTP
# -----------------------------
@app.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():
    if request.method == "POST":
        if request.form["otp"] == session.get("reset_otp"):
            return redirect("/reset")
        return render_template(
            "otp.html",
            error="Invalid OTP"
        )

    return render_template("otp.html")


# -----------------------------
# RESET PASSWORD
# -----------------------------
@app.route("/reset", methods=["GET", "POST"])
def reset():
    if request.method == "POST":
        if "reset_email" not in session:
            return redirect("/forgot")

        new_pass = request.form["password"]
        email = session["reset_email"]

        conn = sqlite3.connect(DB_PATH, timeout=10)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT password FROM users WHERE email=?",
            (email,)
        )
        old_hash = cursor.fetchone()[0]

        if bcrypt.checkpw(
            new_pass.encode(),
            old_hash.encode()
        ):
            conn.close()
            return render_template(
                "reset.html",
                error="New password must be different from old password"
            )

        new_hash = bcrypt.hashpw(
            new_pass.encode(),
            bcrypt.gensalt()
        ).decode()

        cursor.execute(
            "UPDATE users SET password=? WHERE email=?",
            (new_hash, email)
        )

        conn.commit()
        conn.close()
        session.clear()

        flash("Password reset successful. Please login.", "success")
        return redirect("/")

    return render_template("reset.html")


# -----------------------------
# HEALTH FORM
# -----------------------------
@app.route("/health", methods=["POST"])
def health():
    age = int(request.form["age"])
    height = float(request.form["height"])
    weight = float(request.form["weight"])
    goal = request.form["goal"]

    bmi = calculate_bmi(weight, height)
    category = bmi_category(bmi)

    base_cal = daily_calories(weight)
    base_pro = daily_protein(weight)

    if goal == "fat_loss":
        calories = base_cal - 400
        protein = base_pro + 20
        plan_type = "Fat Loss Plan"
    elif goal == "muscle_gain":
        calories = base_cal + 400
        protein = base_pro + 30
        plan_type = "Muscle Gain Plan"
    else:
        calories = base_cal
        protein = base_pro
        plan_type = "Maintenance Plan"

    day, workout = get_today_workout()

    return render_template(
        "dashboard.html",
        age=age,
        height=height,
        weight=weight,
        bmi=round(bmi, 2),
        category=category,
        calories=calories,
        protein=protein,
        plan_type=plan_type,
        day=day,
        muscle=workout["muscle"],
        exercises=workout["exercises"]
    )


# -----------------------------
# LOGOUT
# -----------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# -----------------------------
# WEEKLY PLAN
# -----------------------------
@app.route("/weekly-plan")
def weekly_plan():
    from utils.workouts import WEEKLY_PLAN
    return render_template(
        "weekly_plan.html",
        plan=WEEKLY_PLAN
    )


# -----------------------------
# DOWNLOAD PLAN
# -----------------------------
@app.route("/download-plan")
def download_plan():
    from utils.workouts import WEEKLY_PLAN

    content = "WEEKLY WORKOUT PLAN\n\n"
    for day, data in WEEKLY_PLAN.items():
        content += f"{day} - {data[0]}\n"
        for ex in data[1]:
            content += f"  - {ex}\n"
        content += "\n"

    return Response(
        content,
        mimetype="text/plain",
        headers={
            "Content-Disposition": "attachment; filename=weekly_plan.txt"
        }
    )



# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=10000)

