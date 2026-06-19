from flask import Flask, render_template

app = Flask(__name__)
app.secret_key = "bloom_secret_key"

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