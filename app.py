from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
import sqlite3
import os

app = Flask(__name__)

# Use env var in production; fallback for local dev
app.secret_key = os.getenv("SECRET_KEY", "super_secret_key")

DB_PATH = "signups.db"

# ----------------------
# Admins (simple demo creds)
# ----------------------
ADMINS = {
    "admin1Mpungose": "passInsightForge2025",
    "admin2Bukola": "secure456"
}

# ----------------------
# Database helpers
# ----------------------
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS signups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name   TEXT NOT NULL,
                email  TEXT NOT NULL,
                course TEXT NOT NULL
            )
        """)
        # optional: improve concurrency on Render
        conn.execute("PRAGMA journal_mode=WAL;")

def add_signup(name: str, email: str, course: str) -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO signups (name, email, course) VALUES (?, ?, ?)",
            (name, email, course)
        )

def get_all_signups():
    with get_conn() as conn:
        rows = conn.execute("SELECT name, email, course FROM signups ORDER BY id DESC").fetchall()
        # return list of dicts for easy use in Jinja: signup.name, signup.email, signup.course
        return [dict(row) for row in rows]

# Initialize DB at startup
init_db()

# ----------------------
# Auth decorator
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
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    course = request.form.get("course", "").strip()

    if name and email and course:
        add_signup(name, email, course)
        return render_template("success.html", name=name)
    else:
        flash("Please fill out all fields!", "warning")
        return redirect(url_for("home"))

# Admin login page (hidden route)
@app.route("/secret-admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if username in ADMINS and ADMINS[username] == password:
            session["admin_logged_in"] = username
            flash("Login successful!", "success")
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Invalid credentials!", "danger")

    return render_template("admin_login.html")

# Admin dashboard (hidden route)
@app.route("/hidden-admin-dashboard")
@login_required
def admin_dashboard():
    signups = get_all_signups()
    return render_template("admin_dashboard.html", signups=signups)

# Admin logout
@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("admin_login"))

# Optional: health check endpoint for Render
@app.route("/health")
def health():
    return "ok", 200

if __name__ == "__main__":
    # For local dev only; Render will use gunicorn via Procfile
    app.run(debug=True)
