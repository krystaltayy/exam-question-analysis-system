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