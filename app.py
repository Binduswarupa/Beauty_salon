from flask import Flask, render_template, request, redirect, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid

app = Flask(__name__)
app.secret_key = "local_secret_key"

# ---------------- LOCAL STORAGE (IN-MEMORY) ----------------
users = {}
appointments = []
beauticians = []
contacts = []

# ---------------- HOME ----------------
@app.route("/")
def index():
    return render_template("index.html")

# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]

        if email in users:
            flash("User already exists")
            return redirect("/register")

        users[email] = {
            "name": request.form["name"],
            "password": generate_password_hash(request.form["password"]),
            "created_at": str(datetime.now())
        }

        flash("Registration successful! Please login.")
        return redirect("/login")

    return render_template("register.html")

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        if email in users and check_password_hash(users[email]["password"], password):
            session["user"] = email
            return redirect("/services")

        flash("Invalid email or password")

    return render_template("login.html")

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------------- SERVICES ----------------
@app.route("/services")
def services():
    if "user" not in session:
        return redirect("/login")
    return render_template("services.html")

# ---------------- APPOINTMENTS PAGE ----------------
@app.route("/appointments")
def appointments_page():
    if "user" not in session:
        return redirect("/login")
    return render_template("appointments.html")

# ---------------- BOOK APPOINTMENT ----------------
@app.route("/book", methods=["POST"])
def book():
    if "user" not in session:
        return redirect("/login")

    appointments.append({
        "appointment_id": str(uuid.uuid4()),
        "user": session["user"],
        "service": request.form["service"],
        "beautician": request.form["beautician"],
        "date": request.form["date"],
        "time": request.form["time"],
        "status": "Booked"
    })

    flash("Appointment booked successfully!")
    return redirect("/my-appointments")

# ---------------- MY APPOINTMENTS ----------------
@app.route("/my-appointments")
def my_appointments():
    if "user" not in session:
        return redirect("/login")

    user_apps = [a for a in appointments if a["user"] == session["user"]]
    return render_template("my_appointments.html", appointments=user_apps)

# ---------------- CANCEL APPOINTMENT ----------------
@app.route("/cancel/<appointment_id>")
def cancel(appointment_id):
    global appointments
    appointments = [a for a in appointments if a["appointment_id"] != appointment_id]
    flash("Appointment cancelled")
    return redirect("/my-appointments")

# ---------------- PROFILE ----------------
@app.route("/profile")
def profile():
    if "user" not in session:
        return redirect("/login")

    email = session["user"]
    user_apps = [a for a in appointments if a["user"] == email]

    return render_template(
        "profile.html",
        user={"email": email, "name": users[email]["name"]},
        appointments=user_apps
    )

# ---------------- CONTACT ----------------
@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        contacts.append({
            "name": request.form["name"],
            "email": request.form["email"],
            "message": request.form["message"]
        })
        flash("Message sent successfully!")
        return redirect("/contact")

    return render_template("contact.html")

# ---------------- ADMIN DASHBOARD ----------------
@app.route("/admin-dashboard")
def admin_dashboard():
    return render_template("admin_dashboard.html", appointments=appointments)

# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(debug=True)
