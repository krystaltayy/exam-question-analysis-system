from flask import Flask  # type: ignore[import]
import db
app = Flask(__name__)
db.init_app(app)
# ---WEB ROUTES GO HERE---
@app.route("/")
def home():
    return "<h1>Server is running!</h1><p>Centeralized DB module is active.</p>"
if __name__ == "__main__":
    app.run(debug=True)