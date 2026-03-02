import streamlit as st
import sqlite3
import random

# -----------------------------
# DATABASE SETUP
# -----------------------------
def init_db():
    conn = sqlite3.connect("database_streamlit.db")
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
# SESSION STATE
# -----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.student_id = None
    st.session_state.student_name = None

# -----------------------------
# CSS STYLING
# -----------------------------
st.markdown(
    """
    <style>
    /* Background */
    .stApp {
        background: lightblue;
    }

    /* Center title */
    h1, h2 {
        text-align: center;
        color: #333;
    }

    /* Styled buttons */
    div.stButton > button {
        background-color: #f6c23e;
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        font-weight: bold;
        border: none;
        transition: transform 0.3s;
    }
    div.stButton > button:hover {
        background-color: #dda20a;
        transform: scale(1.05);
        cursor: pointer;
    }

    /* Table styling */
    table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 15px;
    }
    th {
        background-color: #f6c23e;
        color: white;
        padding: 8px;
    }
    td {
        padding: 8px;
        text-align: center;
    }

    /* Input fields */
    input {
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #ccc;
        width: 90%;
        margin-bottom: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# FUNCTIONS
# -----------------------------
def register_user(name, email, password):
    conn = sqlite3.connect("database_streamlit.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
        (name, email, password, "student")
    )
    student_id = cursor.lastrowid
    subjects = ["Mathematics", "Science", "English"]
    for subject in subjects:
        marks = random.randint(50, 100)
        cursor.execute(
            "INSERT INTO results (student_id, subject, marks) VALUES (?, ?, ?)",
            (student_id, subject, marks)
        )
    conn.commit()
    conn.close()
    st.success("Registration successful! You can now login.")

def login_user(email, password):
    conn = sqlite3.connect("database_streamlit.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
    user = cursor.fetchone()
    conn.close()
    if user:
        st.session_state.logged_in = True
        st.session_state.student_id = user[0]
        st.session_state.student_name = user[1]
        return True
    else:
        st.error("Invalid email or password")
        return False

def show_results(student_id):
    conn = sqlite3.connect("database_streamlit.db")
    cursor = conn.cursor()
    cursor.execute("SELECT subject, marks FROM results WHERE student_id=?", (student_id,))
    data = cursor.fetchall()
    conn.close()
    return data

# -----------------------------
# STREAMLIT UI
# -----------------------------
st.title("College ERP System")

menu = ["Login", "Register"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Register":
    st.subheader("Student Registration")
    name = st.text_input("Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Register"):
        if name and email and password:
            register_user(name, email, password)
        else:
            st.warning("Please fill all fields")

if choice == "Login":
    if not st.session_state.logged_in:
        st.subheader("Student Login")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            login_user(email, password)
    else:
        st.subheader(f"Welcome, {st.session_state.student_name}!")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.student_id = None
            st.session_state.student_name = None

if st.session_state.logged_in:
    st.subheader("Dashboard")
    st.write("Click below to see your results:")
    if st.button("View Results"):
        results = show_results(st.session_state.student_id)
        st.table(results)