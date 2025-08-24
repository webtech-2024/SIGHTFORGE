from flask import Flask, render_template, request, redirect, url_for
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

# Admin email config
ADMIN_EMAILS = ["nkosikhonampungose40@gmail.com", "afolayandorcas46@gmail.com"]  # two admin emails
EMAIL_USER = "Afolayandorcas46@gmail.com"  # the email you send from
EMAIL_PASS = "cxoj weil kmbr rdik"    # your email password or app password
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit():
    name = request.form["name"]
    email = request.form["email"]

    subject = "New User Submission"
    body = f"New user submitted info:\n\nName: {name}\nEmail: {email}"

    # Send email to multiple admins
    for admin_email in ADMIN_EMAILS:
        send_email(admin_email, subject, body)

    return redirect(url_for("success"))

@app.route("/success")
def success():
    return render_template("success.html")

def send_email(to_email, subject, body):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, to_email, msg.as_string())

if __name__ == "__main__":
    app.run(debug=True)
