from flask import request, render_template
from web import app
from services.bloom_service import classify_question

@app.route("/analyze", methods=["POST"])
def analyze_question():
    question = request.form.get("question")
    q_type = request.form.get("type")

    level = classify_question(question)

    return render_template("result.html", question=question, level=level)