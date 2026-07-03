import os
from flask import send_file
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime
import pytz
from flask import request, render_template, redirect, url_for, session
from web import app
from services.bloom_service import detect_bloom_level, c1_keywords, c2_keywords
from services.file_service import (
    extract_text_from_docx,
    extract_text_from_pdf,
    extract_text_from_txt,
    split_questions
)
from Database.db import get_db_connection


def get_myt_now():
    myt = pytz.timezone('Asia/Kuala_Lumpur')
    return datetime.now(myt).strftime('%Y-%m-%d %H:%M:%S')


@app.route("/analyze", methods=["POST"])
def analyze_question():

    question = request.form.get("question", "")
    uploaded_file = request.files.get("file")

    # FILE UPLOAD → analyze file and go to dashboard
    if uploaded_file and uploaded_file.filename:

        if "user_id" not in session:
            return render_template(
            "index2.html",
            login_required_popup=True
        )

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
            INSERT INTO uploaded_files (lecturer_id, filename, uploaded_at)
            VALUES (?, ?, ?)
            """,
            (session["user_id"], uploaded_file.filename, get_myt_now())
        )

        file_id = cursor.lastrowid

        for q in questions:

            level = detect_bloom_level(q)

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
          level="Document Analysis",
          file_id=file_id,
          back_url=url_for('home')
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

        level = detect_bloom_level(question)

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
            (lecturer_id, bloom_level_id, question_text, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (session["user_id"], bloom_level_id, question, get_myt_now())
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


@app.route("/history")
def view_history():

    if "user_id" not in session:
        return redirect("/login")

    search = request.args.get("search", "")
    search_pattern = "%" + search + "%"

    conn = get_db_connection()

    single_questions = conn.execute(
        """
        SELECT q.question_text, q.created_at, b.level_name
        FROM questions q
        JOIN blooms_levels b
        ON q.bloom_level_id = b.level_id
        WHERE q.lecturer_id = ?
        AND q.question_text LIKE ?
        ORDER BY q.created_at DESC
        """,
        (session["user_id"], search_pattern)
    ).fetchall()

    uploaded_files = conn.execute(
        """
        SELECT
            uf.id,
            uf.filename,
            uf.uploaded_at,
            COUNT(fq.id) AS question_count
        FROM uploaded_files uf
        LEFT JOIN file_questions fq
        ON uf.id = fq.file_id
        WHERE uf.lecturer_id = ?
        AND uf.filename LIKE ?
        GROUP BY uf.id
        ORDER BY uf.uploaded_at DESC
        """,
        (session["user_id"], search_pattern)
    ).fetchall()

    conn.close()

    return render_template(
        "history.html",
        single_questions=single_questions,
        uploaded_files=uploaded_files,
        search=search
    )


@app.route("/dashboard/<int:file_id>")
def view_file_dashboard(file_id):

    if "user_id" not in session:
        return redirect("/login")

    conn = get_db_connection()

    file = conn.execute(
    """
    SELECT * FROM uploaded_files
    WHERE id = ?
    AND lecturer_id = ?
    """,
    (file_id, session["user_id"])
    ).fetchone()

    if not file:
      conn.close()
      return redirect("/history")

    file_questions = conn.execute(
        """
        SELECT fq.question_text, b.level_name
        FROM file_questions fq
        LEFT JOIN blooms_levels b
        ON fq.bloom_level_id = b.level_id
        WHERE fq.file_id = ?
        """,
        (file_id,)
    ).fetchall()

    conn.close()

    results = []

    c1_count = 0
    c2_count = 0

    for q in file_questions:
        if q["level_name"] == "Remembering":
            c1_count += 1
            level = "Cognitive 1 - Remember"
        elif q["level_name"] == "Understanding":
            c2_count += 1
            level = "Cognitive 2 - Understand"
        else:
            level = "No Match"

        results.append({
            "question": q["question_text"],
            "level": level
        })

    total = c1_count + c2_count

    c1_percent = round((c1_count / total) * 100) if total > 0 else 0
    c2_percent = round((c2_count / total) * 100) if total > 0 else 0

    return render_template(
    "dashboard.html",
    question=file["filename"],
    results=results,
    c1_percent=c1_percent,
    c2_percent=c2_percent,
    level="Document Analysis",
    file_id=file_id,
    back_url=url_for('view_history')
)

@app.route("/export_pdf/<int:file_id>")
def export_pdf(file_id):

    if "user_id" not in session:
        return redirect("/login")

    conn = get_db_connection()

    file = conn.execute(
        """
        SELECT *
        FROM uploaded_files
        WHERE id = ?
        AND lecturer_id = ?
        """,
        (file_id, session["user_id"])
    ).fetchone()

    if not file:
        conn.close()
        return redirect("/history")

    file_questions = conn.execute(
        """
        SELECT fq.question_text, b.level_name
        FROM file_questions fq
        LEFT JOIN blooms_levels b
        ON fq.bloom_level_id = b.level_id
        WHERE fq.file_id = ?
        """,
        (file_id,)
    ).fetchall()

    conn.close()

    c1_count = 0
    c2_count = 0

    for q in file_questions:
        if q["level_name"] == "Remembering":
            c1_count += 1
        elif q["level_name"] == "Understanding":
            c2_count += 1

    total = c1_count + c2_count

    c1_percent = round((c1_count / total) * 100) if total > 0 else 0
    c2_percent = round((c2_count / total) * 100) if total > 0 else 0

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Bloom Taxonomy Analysis Report", styles["Title"]))
    elements.append(Spacer(1, 20))

    elements.append(Paragraph(f"<b>Filename:</b> {file['filename']}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Date Uploaded:</b> {file['uploaded_at']}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Cognitive 1 - Remember:</b> {c1_percent}%", styles["Normal"]))
    elements.append(Paragraph(f"<b>Cognitive 2 - Understand:</b> {c2_percent}%", styles["Normal"]))
    elements.append(Spacer(1, 20))

    data = [["No.", "Question", "Bloom Level"]]

    for i, q in enumerate(file_questions, start=1):

        if q["level_name"] == "Remembering":
            level = "Cognitive 1 - Remember"
        elif q["level_name"] == "Understanding":
            level = "Cognitive 2 - Understand"
        else:
            level = "No Match"

        data.append([
            str(i),
            Paragraph(q["question_text"], styles["Normal"]),
            level
        ])

    table = Table(data, colWidths=[40, 360, 120])

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#ff8da1")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#fff4f7")]),
    ]))

    elements.append(table)

    doc.build(elements)

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"{file['filename']}_analysis_report.pdf",
        mimetype="application/pdf"
    )