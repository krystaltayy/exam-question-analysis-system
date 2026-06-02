import os
from services.file_service import extract_text_from_docx, split_questions
from flask import request, render_template
from web import app
from services.bloom_service import classify_question
from Database.db import get_db_connection


@app.route("/analyze", methods=["POST"])
def analyze_question():

    question = request.form.get("question")
    uploaded_file = request.files.get("pdf_file")

    print("UPLOADED FILE:", uploaded_file)

    if uploaded_file:
      print("FILENAME:", uploaded_file.filename)

    if uploaded_file and uploaded_file.filename != "":
        upload_folder = "uploads"

        if not os.path.exists(upload_folder):
          os.makedirs(upload_folder)

        file_path = os.path.join(upload_folder, uploaded_file.filename)
        uploaded_file.save(file_path)
        text = extract_text_from_docx(file_path)
        print(text)
        questions = split_questions(text)

        results = []

        for q in questions:
          level = classify_question(q)

          results.append({
            "question": q,
            "level": level
          })

        return render_template(
          "index2.html",
          results=results
        )

        question = f"File uploaded: {uploaded_file.filename}"
    # validate question length
    word_count = len(question.split())

    if word_count < 2:

      error = "Please enter a complete question (at least 2 words)."

      return render_template(
      "index2.html",
      error=error
    )
    q_type = request.form.get("type")

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
    result = level
   

    return render_template(
    "index2.html",
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


      
