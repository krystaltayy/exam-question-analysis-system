from flask import request, render_template
from web import app
from services.bloom_service import classify_question

@app.route("/analyze", methods=["POST"])
def analyze_question():

    question = request.form.get("question", "")
    uploaded_file = request.files.get("file")

    print("QUESTION:", question)
    print("FILENAME:", uploaded_file.filename if uploaded_file else "None")

    # FILE UPLOAD → go to dashboard
    if uploaded_file and uploaded_file.filename:
        print(">>> Going to dashboard")
        return render_template(
            "dashboard.html",
            question=uploaded_file.filename,
            level="File uploaded successfully",
            q_type="Document"
        )

    # SINGLE QUESTION → stay on index2.html
    if question.strip():
        print(">>> Going to index2")
        level = classify_question(question)

        if not level:
            level = "No level detected"

        return render_template(
            "index2.html",
            question=question,
            level=level,
            q_type="General"
        )

    # NOTHING ENTERED
    print(">>> Nothing entered")
    return render_template("index2.html")