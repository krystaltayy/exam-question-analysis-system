from flask import request, render_template
from web import app
from services.bloom_service import classify_question, c1_keywords, c2_keywords
from Database.db import get_db_connection


@app.route("/analyze", methods=["POST"])
def analyze_question():
    question = request.form.get("question", "")
    uploaded_file = request.files.get("file")

    # FILE UPLOAD → go to dashboard
    if uploaded_file and uploaded_file.filename:
        return render_template(
            "dashboard.html",
            question=uploaded_file.filename,
            level="File uploaded successfully",
            q_type="Document"
        )

    # SINGLE QUESTION → stay on index2.html
    if question.strip():
        # Validate word count
        word_count = len(question.split())
        if word_count < 2:
            error = "Please enter a complete question (at least 2 words)."
            return render_template("index2.html", error=error)

        # Validate keyword
        all_keywords = c1_keywords + c2_keywords
        question_lower = question.lower()
        has_keyword = any(keyword in question_lower for keyword in all_keywords)

        if not has_keyword:
            error = "Please enter a valid question."
            return render_template("index2.html", error=error)

        # Classify
        level = classify_question(question)
        if not level:
            level = "No level detected"

        # Save to database
        if level == "C1 - Remember":
            bloom_level_id = 1
        elif level == "C2 - Understand":
            bloom_level_id = 2
        else:
            bloom_level_id = 0

        conn = get_db_connection()
        conn.execute(
            """
            INSERT INTO questions
            (lecturer_id, bloom_level_id, question_text)
            VALUES (?, ?, ?)
            """,
            (1, bloom_level_id, question)
        )
        conn.commit()
        conn.close()

        return render_template(
            "index2.html",
            question=question,
            level=level,
            q_type="General"
        )

    # NOTHING ENTERED
    return render_template("index2.html")


@app.route("/questions")
def view_questions():
    conn = get_db_connection()
    questions = conn.execute("SELECT * FROM questions").fetchall()
    conn.close()
    return render_template("questions.html", questions=questions)