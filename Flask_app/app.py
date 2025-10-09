from flask import Flask, render_template, request, redirect, session
import json

app = Flask(__name__)
app.secret_key = "superhemlig_nyckel"

def load_users():
    with open("users.json", "r") as f:
        return json.load(f)

def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f, indent=4)

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        users = load_users()
        if username in users and users[username]["password"] == password:
            session["username"] = username
            session["role"] = users[username]["role"]
            return redirect("/dashboard")
        return "Fel användarnamn eller lösenord"
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect("/")
    return render_template("dashboard.html", user=session["username"])

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if session.get("role") != "admin":
        return "Endast admin har tillgång till denna sida"
    
    users = load_users()

    if request.method == "POST":
        new_user = request.form["new_user"]
        new_pass = request.form["new_pass"]
        role = request.form["role"]
        users[new_user] = {"password": new_pass, "role": role}
        save_users(users)
        return redirect("/admin")

    return render_template("admin.html", users=users)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")