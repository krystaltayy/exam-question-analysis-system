from flask import request, render_template
from web import app
from services.bloom_service import classify_question

@app.route("/analyze", methods=["POST"])
def analyze_question():

    question = request.form.get("question")
    print("QUESTION:", question)

    q_type = "General"

    level = classify_question(question)

    if not level:
        level = "No level detected"

    return render_template(
        "index2.html",
        question=question,
        level=level,
        q_type=q_type
    )