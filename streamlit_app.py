
import streamlit as st
import sqlite3
import pandas as pd

st.title("Student Records")

# Connect to the database
conn = sqlite3.connect("students.db")

# Create a table
conn.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        course TEXT
    )
""")
conn.commit()

# Form to add a student
name = st.text_input("Student Name")
course = st.selectbox(
    "Course", ["Python", "AI", "Web Development"]
)

if st.button("Save Student"):
    if name.strip():
        conn.execute(
            "INSERT INTO students (name, course) VALUES (?, ?)",
            (name.strip(), course)
        )
        conn.commit()
        st.success("Student saved!")
        st.rerun()
    else:
        st.warning("Enter a student name.")

# Read and display saved students
data = pd.read_sql_query(
    "SELECT * FROM students", conn
)

st.subheader("Saved Students")
st.dataframe(data, hide_index=True)

conn.close()
