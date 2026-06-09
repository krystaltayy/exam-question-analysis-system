import os
from flask import request, render_template
from web import app
from services.bloom_service import classify_question, c1_keywords, c2_keywords
from services.file_service import (
    extract_text_from_docx,
    extract_text_from_pdf,
    extract_text_from_txt,
    split_questions
)
from Database.db import get_db_connection


@app.route("/analyze", methods=["POST"])
def analyze_question():

    question = request.form.get("question", "")
    uploaded_file = request.files.get("file")

    # FILE UPLOAD → analyze file and go to dashboard
    if uploaded_file and uploaded_file.filename:

        upload_folder = "uploads"

        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        file_path = os.path.join(upload_folder, uploaded_file.filename)
        uploaded_file.save(file_path)

        filename = uploaded_file.filename.lower()

        if filename.endswith(".docx"):
            text = extract_text_from_docx(file_path)
        elif filename.endswith(".pdf"):
            text = extract_text_from_pdf(file_path)
        elif filename.endswith(".txt"):
            text = extract_text_from_txt(file_path)
        else:
            return render_template(
                "index2.html",
                error="Unsupported file type. Please upload DOCX, PDF, or TXT file."
            )

        questions = split_questions(text)

        results = []
        c1_count = 0
        c2_count = 0

        conn = get_db_connection()

        cursor = conn.execute(
            """
            INSERT INTO uploaded_files (lecturer_id, filename)
            VALUES (?, ?)
            """,
            (1, uploaded_file.filename)
        )

        file_id = cursor.lastrowid

        for q in questions:

            level = classify_question(q)

            if level == "C1 - Remember":
                c1_count += 1
                bloom_level_id = 1
                display_level = "Cognitive 1 - Remember"
            elif level == "C2 - Understand":
                c2_count += 1
                bloom_level_id = 2
                display_level = "Cognitive 2 - Understand"
            else:
                bloom_level_id = 0
                display_level = level

            conn.execute(
                """
                INSERT INTO file_questions
                (file_id, question_text, bloom_level_id)
                VALUES (?, ?, ?)
                """,
                (file_id, q, bloom_level_id)
            )

            results.append({
                "question": q,
                "level": display_level
            })

        conn.commit()
        conn.close()

        total = c1_count + c2_count

        if total > 0:
            c1_percent = round((c1_count / total) * 100)
            c2_percent = round((c2_count / total) * 100)
        else:
            c1_percent = 0
            c2_percent = 0

        return render_template(
            "dashboard.html",
            question=uploaded_file.filename,
            results=results,
            c1_percent=c1_percent,
            c2_percent=c2_percent,
            level="Document Analysis"
        )

    # SINGLE QUESTION → stay on index2.html
    if question.strip():

        word_count = len(question.split())

        if word_count < 2:
            error = "Please enter a complete question (at least 2 words)."
            return render_template("index2.html", error=error)

        all_keywords = c1_keywords + c2_keywords
        question_lower = question.lower()

        has_keyword = any(keyword in question_lower for keyword in all_keywords)

        if not has_keyword:
            error = "Please enter a valid question."
            return render_template("index2.html", error=error)

        level = classify_question(question)

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

    return render_template("index2.html")


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