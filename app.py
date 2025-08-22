from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps

app = Flask(__name__)
app.secret_key = "super_secret_key"  # change to a long random string in production

# Store signups in memory
signups = []

# Define two admins (username, password)
ADMINS = {
    "admin1Mpungose": "passInsightForge2025",
    "admin2Bukola": "secure456"
}

# ----------------------
# Decorator: login required
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

    if name and email:
        signups.append({"name": name, "email": email})
        return render_template("success.html", name=name)
    else:
        flash("Please fill out all fields!", "warning")
        return redirect(url_for("home"))


# Admin login page
@app.route("/secret-admin-login", methods=["GET", "POST"])  # hidden login route
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


# Admin dashboard (list of signups)
@app.route("/hidden-admin-dashboard")  # hidden dashboard route
@login_required
def admin_dashboard():
    return render_template("admin_dashboard.html", signups=signups)


# Admin logout
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('admin_login'))


if __name__ == "__main__":
    app.run(debug=True)
