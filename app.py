from flask import Flask, render_template, request, redirect, session
import sqlite3
import random  # <-- added for random marks

app = Flask(__name__)
app.secret_key = "secretkey"

# -----------------------------
# DATABASE SETUP
# -----------------------------
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        subject TEXT,
        marks INTEGER
    )
    """)

    conn.commit()
    conn.close()

init_db()

# -----------------------------
# ROUTES
# -----------------------------

@app.route('/')
def login():
    return render_template("login.html")


@app.route('/login', methods=['POST'])
def login_user():
    email = request.form['email']
    password = request.form['password']

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        session['student_id'] = user[0]
        return redirect("/dashboard")
    else:
        return "Invalid Login"


@app.route('/register')
def register():
    return render_template("register.html")


@app.route('/register_user', methods=['POST'])
def register_user():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Insert student
    cursor.execute(
        "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
        (name, email, password, "student")
    )
    student_id = cursor.lastrowid

    # Automatically add subjects & random marks
    subjects = ["Mathematics", "Science", "English"]
    for subject in subjects:
        marks = random.randint(50, 100)  # random marks between 50 and 100
        cursor.execute(
            "INSERT INTO results (student_id, subject, marks) VALUES (?, ?, ?)",
            (student_id, subject, marks)
        )

    conn.commit()
    conn.close()

    return redirect("/")


@app.route('/dashboard')
def dashboard():
    if 'student_id' in session:
        return render_template("dashboard.html")
    return redirect("/")


@app.route('/results')
def results():
    if 'student_id' not in session:
        return redirect("/")

    student_id = session['student_id']

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT subject, marks FROM results WHERE student_id=?", (student_id,))
    data = cursor.fetchall()
    conn.close()

    print("Logged student ID:", student_id)
    print("Fetched data:", data)

    return render_template("results.html", results=data)


@app.route('/logout')
def logout():
    session.clear()
    return redirect("/")


import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)