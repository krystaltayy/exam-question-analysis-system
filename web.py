from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
import os

app.secret_key = os.environ.get("SECRET_KEY", "dev_secret_key")

@app.route("/")
def home():
    return render_template("index2.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route('/index2')
def index2():
    return render_template('index2.html')


from routes.question_routes import *
from routes.auth_routes import *

if __name__ == "__main__":
    app.run(debug=True, port=5001)