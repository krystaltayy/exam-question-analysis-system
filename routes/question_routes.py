from flask import request, render_template
from web import app
from services.bloom_service import classify_question
from Database.db import get_db_connection


@app.route("/analyze", methods=["POST"])
def analyze_question():

    question = request.form.get("question")
    q_type = request.form.get("type")

    level = classify_question(question)

    # Convert Bloom level to database ID
    if level == "C1 - Remember":
        bloom_level_id = 1
    elif level == "C2 - Understand":
        bloom_level_id = 2
    else:
        bloom_level_id = 0

    # Temporary lecturer ID
    lecturer_id = 1

    # Save into database
    conn = get_db_connection()

    conn.execute(
        """
        INSERT INTO questions
        (lecturer_id, bloom_level_id, question_text)
        VALUES (?, ?, ?)
        """,
        (lecturer_id, bloom_level_id, question)
    )

    conn.commit()
    conn.close()

    return render_template(
        "result.html",
        question=question,
        level=level,
        q_type=q_type
    )