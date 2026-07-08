from flask import request, render_template, redirect, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
from web import app
from Database.db import get_db_connection
import random
import string
import secrets
import re
from datetime import datetime, timedelta

# Mail config
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
import os
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("MAIL_USERNAME")

mail = Mail(app)


def generate_code():
    return ''.join(random.choices(string.digits, k=6))


@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        password_hash = generate_password_hash(password, method="pbkdf2:sha256")

        conn = get_db_connection()

        existing_user = conn.execute(
            "SELECT * FROM users WHERE email = ? OR username = ?",
            (email, username)
        ).fetchone()

        if existing_user:
            conn.close()
            return render_template(
                "signup.html",
                error="Username or email already exists. Please log in."
            )

        code = generate_code()

        conn.execute(
            """
            INSERT INTO users (username, email, password_hash, is_verified, verification_code)
            VALUES (?, ?, ?, 0, ?)
            """,
            (username, email, password_hash, code)
        )

        conn.commit()
        conn.close()

        # Send verification email
        msg = Message("Your Verification Code", recipients=[email])
        msg.body = f"Hi {username},\n\nYour verification code is: {code}\n\nEnter this code to activate your account."
        mail.send(msg)

        session["pending_email"] = email

        return redirect("/verify")

    return render_template("signup.html")


@app.route("/verify", methods=["GET", "POST"])
def verify():

    email = session.get("pending_email")

    if not email:
        return redirect("/signup")

    if request.method == "POST":
        code = request.form.get("code")

        conn = get_db_connection()

        user = conn.execute(
            "SELECT * FROM users WHERE email = ? AND verification_code = ?",
            (email, code)
        ).fetchone()

        if not user:
            conn.close()
            return render_template("verify.html", error="Invalid code. Please try again.")

        conn.execute(
            "UPDATE users SET is_verified = 1, verification_code = NULL WHERE email = ?",
            (email,)
        )

        conn.commit()
        conn.close()

        session.pop("pending_email", None)

        return render_template("verify.html", success=True)

    return render_template("verify.html")


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

        if not user or not check_password_hash(user["password_hash"], password):
            return render_template("signup.html", error="Invalid email or password.")

        if not user["is_verified"]:
            session["pending_email"] = email
            return redirect("/verify")

        session["user_id"] = user["id"]
        session["username"] = user["username"]
        session["email"] = user["email"]
        session["created_at"] = user["created_at"]
        return redirect("/")

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
        password_hash = generate_password_hash(password, method="pbkdf2:sha256")

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

        # Check email format first
        email_pattern = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
        if not email or not re.match(email_pattern, email):
            return render_template(
                "forgot_password.html",
                error="Please enter a valid email address."
            )

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

        token = secrets.token_urlsafe(32)
        expiry = (datetime.now() + timedelta(minutes=30)).isoformat()

        conn.execute(
            """
            UPDATE users
            SET reset_token = ?, reset_token_expiry = ?
            WHERE email = ?
            """,
            (token, expiry, email)
        )

        conn.commit()
        conn.close()

        reset_link = url_for("reset_password", token=token, _external=True)

        msg = Message("Reset Your Password", recipients=[email])
        msg.body = f"Hi,\n\nClick the link below to reset your password. This link expires in 30 minutes.\n\n{reset_link}\n\nIf you didn't request this, ignore this email."
        mail.send(msg)

        return render_template(
            "forgot_password.html",
            success="A reset link has been sent to your email."
        )

    return render_template("forgot_password.html")


@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):

    conn = get_db_connection()

    user = conn.execute(
        "SELECT * FROM users WHERE reset_token = ?",
        (token,)
    ).fetchone()

    if not user:
        conn.close()
        return render_template("reset_password.html", error="Invalid or expired link.", invalid=True)

    expiry = datetime.fromisoformat(user["reset_token_expiry"])

    if datetime.now() > expiry:
        conn.close()
        return render_template("reset_password.html", error="This link has expired.", invalid=True)

    if request.method == "POST":
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        if new_password != confirm_password:
            conn.close()
            return render_template("reset_password.html", error="Passwords do not match.", token=token)

        new_password_hash = generate_password_hash(new_password, method="pbkdf2:sha256")

        conn.execute(
            """
            UPDATE users
            SET password_hash = ?, reset_token = NULL, reset_token_expiry = NULL
            WHERE id = ?
            """,
            (new_password_hash, user["id"])
        )

        conn.commit()
        conn.close()

        return render_template("reset_password.html", success="Password reset successfully. You can now log in.")

    conn.close()
    return render_template("reset_password.html", token=token)