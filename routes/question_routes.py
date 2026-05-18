
from flask import request, render_template
from web import app
from services.bloom_service import classify_question
from Database.db import get_db_connection


@app.route("/analyze", methods=["POST"])
def analyze_question():

    question = request.form.get("question")
    q_type = request.form.get("type")

    print("DEBUG QUESTION:", question)

    # 1. classify first
    level = classify_question(question)

    # 2. convert to DB id
    if level == "C1 - Remember":
        bloom_level_id = 1
    elif level == "C2 - Understand":
        bloom_level_id = 2
    else:
        bloom_level_id = 0

    # 3. save to database
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

    # 4. show result on SAME PAGE
    result = f"{level}"
    print("RESULT SENT TO HTML:", result)

    return render_template("home.html", result=result, question=question)

    return render_template(
        "result.html",
        question=question,
        level=level,
        q_type=q_type
    )

@app.route("/questions")
def view_questions():

    conn = get_db_connection()

    questions = conn.execute(
        "SELECT * FROM questions"
    ).fetchall()

    conn.close()

    return render_template(
        "questions.html",
        questions=questions
    )

print(app.url_map)
      