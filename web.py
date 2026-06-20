from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)

@app.route("/")
def home():
   return render_template("index2.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route('/index2')
def index2():
    return render_template('index2.html')

@app.route("/profile")
def profile():
    return render_template("profile.html")

@app.route("/profile/update", methods=["POST"])
def profile_update():
    return redirect(url_for('profile'))

from routes.question_routes import *

if __name__ == "__main__":
    app.run(debug=True, port=5001)