from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import pickle
import re
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "traffic_secret"

# Load model
model = pickle.load(open("traffic_model.pkl", "rb"))

# ================= DATABASE =================
def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        mobile TEXT,
        username TEXT UNIQUE,
        email TEXT UNIQUE,
        password TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ================= ROUTES =================

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/login")
def login():
    return render_template("login.html")

# ================= REGISTER =================

@app.route("/register", methods=["POST"])
def register():

    name = request.form["name"]
    mobile = request.form["mobile"]
    username = request.form["username"]
    email = request.form["email"]
    password = request.form["password"]
    confirm_password = request.form["confirm_password"]

    # VALIDATIONS
    if password != confirm_password:
        flash("Passwords do not match", "error")
        return redirect("/signup")

    if not re.match(r"^[6-9]\d{9}$", mobile):
        flash("Enter valid 10-digit mobile number", "error")
        return redirect("/signup")

    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        flash("Enter valid email address", "error")
        return redirect("/signup")

    if len(password) < 6:
        flash("Password must be at least 6 characters", "error")
        return redirect("/signup")

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # CHECK USERNAME
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    if cursor.fetchone():
        flash("Username already exists", "error")
        conn.close()
        return redirect("/signup")

    # CHECK EMAIL
    cursor.execute("SELECT * FROM users WHERE email=?", (email,))
    if cursor.fetchone():
        flash("Email already registered", "error")
        conn.close()
        return redirect("/signup")

    # HASH PASSWORD
    hashed_password = generate_password_hash(password)

    cursor.execute(
        "INSERT INTO users(name,mobile,username,email,password) VALUES(?,?,?,?,?)",
        (name, mobile, username, email, hashed_password)
    )

    conn.commit()
    conn.close()

    flash("Account created successfully", "success")
    return redirect("/login")

# ================= LOGIN =================

@app.route("/login_user", methods=["POST"])
def login_user():

    username = request.form["username"]
    password = request.form["password"]

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("SELECT name, password FROM users WHERE username=?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user[1], password):
        session["user"] = user[0]
        return redirect("/traffic")

    flash("Incorrect username or password", "error")
    return redirect("/login")

# ================= TRAFFIC =================

@app.route("/traffic")
def traffic():
    if "user" not in session:
        return redirect("/login")

    return render_template("traffic.html", name=session["user"])

# ================= LOGOUT =================

@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Logged out successfully", "success")
    return redirect("/login")

# ================= ANALYTICS =================

@app.route("/analytics")
def analytics():

    if "user" not in session:
        return redirect("/login")

    return render_template("analytics.html")

# ================= PREDICTION =================

@app.route("/predict", methods=["POST"])
def predict():

    temp = float(request.form["temp"])
    rain = float(request.form["rain"])
    snow = float(request.form["snow"])
    clouds = float(request.form["clouds"])
    hour = int(request.form["hour"])

    data = [[temp, rain, snow, clouds, hour]]

    prediction = model.predict(data)
    probability = model.predict_proba(data)

    free_prob = round(probability[0][0]*100,2)
    mod_prob = round(probability[0][1]*100,2)
    cong_prob = round(probability[0][2]*100,2)

    if prediction[0] == 0:
        result = "Free Flow Traffic"
    elif prediction[0] == 1:
        result = "Moderate Traffic"
    else:
        result = "Heavy Congestion"

    return render_template("result.html",
        prediction=result,
        free_prob=free_prob,
        mod_prob=mod_prob,
        cong_prob=cong_prob
    )

if __name__ == "__main__":
    app.run(debug=True)