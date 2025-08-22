from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
import sqlite3

app = Flask(__name__)
app.secret_key = "super_secret_key"

# Define admins
ADMINS = {
    "admin1Mpungose": "passInsightForge2025",
    "admin2Bukola": "secure456"
}

# ----------------------
# Database helper functions
# ----------------------
def init_db():
    conn = sqlite3.connect("signups.db")
    # Create table with course column
    conn.execute("""
        CREATE TABLE IF NOT EXISTS signups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            course TEXT NOT NULL
        )
    """)
    conn.close()

def add_signup(name, email):
    conn = sqlite3.connect("signups.db")
    conn.execute("INSERT INTO signups (name, email) VALUES (?, ?)", (name, email))
    conn.commit()
    conn.close()

def get_all_signups():
    conn = sqlite3.connect("signups.db")
    cursor = conn.execute("SELECT name, email FROM signups")
    rows = cursor.fetchall()
    conn.close()
    return [{"name": row[0], "email": row[1]} for row in rows]

init_db()

# ----------------------
# Login required decorator
# ----------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "admin_logged_in" not in session:
            flash("You must log in as admin first.", "danger")
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated_function

# ----------------------
# Routes
# ----------------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("name")
    email = request.form.get("email")
    course = request.form.get("course")  # NEW

    if name and email and course:
        conn = sqlite3.connect("signups.db")
        conn.execute("INSERT INTO signups (name, email, course) VALUES (?, ?, ?)", (name, email, course))
        conn.commit()
        conn.close()
        return render_template("success.html", name=name)
    else:
        flash("Please fill out all fields!", "warning")
        return redirect(url_for("home"))


@app.route("/secret-admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username in ADMINS and ADMINS[username] == password:
            session["admin_logged_in"] = username
            flash("Login successful!", "success")
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Invalid credentials!", "danger")

    return render_template("admin_login.html")

@app.route("/hidden-admin-dashboard")
@login_required
def admin_dashboard():
    signups = get_all_signups()  # fetch from DB
    return render_template("admin_dashboard.html", signups=signups)

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('admin_login'))

if __name__ == "__main__":
    app.run(debug=True)
