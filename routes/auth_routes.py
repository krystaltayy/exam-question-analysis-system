from flask import request, render_template, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from web import app
from Database.db import get_db_connection


@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        password_hash = generate_password_hash(password)

        conn = get_db_connection()

        existing_user = conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        if existing_user:
            conn.close()
            return render_template(
                "signup.html",
                error="Email already exists. Please log in."
            )

        conn.execute(
            """
            INSERT INTO users (username, email, password_hash)
            VALUES (?, ?, ?)
            """,
            (username, email, password_hash)
        )

        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        conn = get_db_connection()

        user = conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        conn.close()

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["email"] = user["email"]
            session["created_at"] = user["created_at"]
            return redirect("/")

        return render_template(
            "signup.html",
            error="Invalid email or password."
        )

    return render_template("signup.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/profile")
def profile():

    if "user_id" not in session:
        return redirect("/login")

    conn = get_db_connection()

    user = conn.execute(
        "SELECT * FROM users WHERE id = ?",
        (session["user_id"],)
    ).fetchone()

    question_count = conn.execute(
    """
    SELECT COUNT(*)
    FROM questions
    WHERE lecturer_id = ?
    """,
    (session["user_id"],)
    ).fetchone()[0]

    file_count = conn.execute(
    """
    SELECT COUNT(*)
    FROM uploaded_files
    WHERE lecturer_id = ?
    """,
    (session["user_id"],)
    ).fetchone()[0]

    conn.close()

    if not user:
        return redirect("/login")

    session["username"] = user["username"]
    session["email"] = user["email"]
    session["created_at"] = user["created_at"]

    return render_template(
    "profile.html",
    question_count=question_count,
    file_count=file_count
    )


@app.route("/profile/update", methods=["POST"])
def update_profile():

    if "user_id" not in session:
        return redirect("/login")

    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")

    conn = get_db_connection()

    existing_user = conn.execute(
        """
        SELECT * FROM users
        WHERE (username = ? OR email = ?)
        AND id != ?
        """,
        (username, email, session["user_id"])
    ).fetchone()

    if existing_user:
        conn.close()
        return render_template(
            "profile.html",
            error="Username or email already exists."
        )

    if password and password.strip():
        password_hash = generate_password_hash(password)

        conn.execute(
            """
            UPDATE users
            SET username = ?, email = ?, password_hash = ?
            WHERE id = ?
            """,
            (username, email, password_hash, session["user_id"])
        )
    else:
        conn.execute(
            """
            UPDATE users
            SET username = ?, email = ?
            WHERE id = ?
            """,
            (username, email, session["user_id"])
        )

    conn.commit()
    conn.close()

    session["username"] = username
    session["email"] = email

    return redirect("/profile")

@app.route("/delete_account", methods=["POST"])
def delete_account():

    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    conn = get_db_connection()

    conn.execute(
        "DELETE FROM file_questions WHERE file_id IN (SELECT id FROM uploaded_files WHERE lecturer_id = ?)",
        (user_id,)
    )

    conn.execute(
        "DELETE FROM uploaded_files WHERE lecturer_id = ?",
        (user_id,)
    )

    conn.execute(
        "DELETE FROM questions WHERE lecturer_id = ?",
        (user_id,)
    )

    conn.execute(
        "DELETE FROM users WHERE id = ?",
        (user_id,)
    )

    conn.commit()
    conn.close()

    session.clear()

    return redirect("/signup")


@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():

    if request.method == "POST":
        email = request.form.get("email")
        new_password = request.form.get("new_password")

        conn = get_db_connection()

        user = conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        if not user:
            conn.close()
            return render_template(
                "forgot_password.html",
                error="Email not found."
            )

        new_password_hash = generate_password_hash(new_password)

        conn.execute(
            """
            UPDATE users
            SET password_hash = ?
            WHERE email = ?
            """,
            (new_password_hash, email)
        )

        conn.commit()
        conn.close()

        return render_template(
            "forgot_password.html",
            success="Password reset successfully. You can now log in."
        )

    return render_template("forgot_password.html")