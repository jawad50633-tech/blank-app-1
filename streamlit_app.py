
import streamlit as st
import sqlite3
import pandas as pd

# ---------- PAGE CONFIGURATION ----------
st.set_page_config(
    page_title="Student Management System",
    page_icon="🎓",
    layout="wide"
)

# ---------- DATABASE ----------
# Connect to a local SQLite database.
# The database file is created automatically.
def connect_db():
    return sqlite3.connect("students.db")

# Create the students table if it doesn't exist.
def create_table():
    with connect_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                roll_no TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                course TEXT NOT NULL,
                age INTEGER NOT NULL,
                marks REAL NOT NULL
            )
        """)

create_table()


# ---------- HELPER FUNCTIONS ----------
def get_students():
    with connect_db() as conn:
        return pd.read_sql_query(
            "SELECT * FROM students ORDER BY id DESC",
            conn
        )


def add_student(roll, name, course, age, marks):
    with connect_db() as conn:
        conn.execute("""
            INSERT INTO students
            (roll_no, name, course, age, marks)
            VALUES (?, ?, ?, ?, ?)
        """, (roll, name, course, age, marks))


def update_student(student_id, roll, name, course, age, marks):
    with connect_db() as conn:
        conn.execute("""
            UPDATE students
            SET roll_no=?, name=?, course=?, age=?, marks=?
            WHERE id=?
        """, (roll, name, course, age, marks, student_id))


def delete_student(student_id):
    with connect_db() as conn:
        conn.execute(
            "DELETE FROM students WHERE id=?",
            (student_id,)
        )


def grade(marks):
    if marks >= 80:
        return "A"
    elif marks >= 70:
        return "B"
    elif marks >= 60:
        return "C"
    elif marks >= 50:
        return "D"
    return "F"


# ---------- SIDEBAR ----------
st.sidebar.title("🎓 Student Portal")

page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Add Student", "View Students",
     "Edit Student", "Delete Student"]
)

st.sidebar.caption("Student Management System")


# ---------- DASHBOARD ----------
if page == "Dashboard":
    st.title("🎓 Student Management Dashboard")
    st.write("Manage student records in one place.")

    df = get_students()

    total = len(df)
    average = df["marks"].mean() if total else 0
    passed = int((df["marks"] >= 50).sum()) if total else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Students", total)
    c2.metric("Average Marks", f"{average:.1f}")
    c3.metric("Passed Students", passed)

    if total:
        st.subheader("Students by Course")
        st.bar_chart(df["course"].value_counts())

        st.subheader("Recent Student Records")
        st.dataframe(
            df[["roll_no", "name", "course", "marks"]],
            use_container_width=True
        )
    else:
        st.info("No students added yet. Start with Add Student.")


# ---------- ADD STUDENT ----------
elif page == "Add Student":
    st.title("➕ Add New Student")

    with st.form("add_form"):
        roll = st.text_input("Roll Number")
        name = st.text_input("Full Name")
        course = st.selectbox(
            "Course",
            ["Python", "Artificial Intelligence",
             "Web Development", "Cybersecurity"]
        )
        age = st.number_input("Age", 5, 100, 18)
        marks = st.number_input("Marks", 0.0, 100.0, 0.0)

        submitted = st.form_submit_button("Save Student")

    if submitted:
        if not roll.strip() or not name.strip():
            st.error("Roll number and name are required.")
        else:
            try:
                add_student(
                    roll.strip(), name.strip(),
                    course, age, marks
                )
                st.success("Student added successfully!")
            except sqlite3.IntegrityError:
                st.error("This roll number already exists.")


# ---------- VIEW STUDENTS ----------
elif page == "View Students":
    st.title("📋 All Students")

    df = get_students()

    if not df.empty:
        search = st.text_input(
            "Search by name, roll number, or course"
        )

        if search:
            mask = df[
                ["name", "roll_no", "course"]
            ].apply(
                lambda col: col.str.contains(
                    search, case=False, na=False
                )
            ).any(axis=1)

            df = df[mask]

        df["grade"] = df["marks"].apply(grade)

        st.write(f"Records found: {len(df)}")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No student records found.")


# ---------- EDIT STUDENT ----------
elif page == "Edit Student":
    st.title("✏️ Edit Student")

    df = get_students()

    if df.empty:
        st.info("Add a student before editing.")
    else:
        # Use database IDs to identify records.
        student_ids = df["id"].tolist()

        selected_id = st.selectbox(
            "Select Student",
            student_ids,
            format_func=lambda sid: (
                f"{df.loc[df['id'] == sid, 'roll_no'].iloc[0]} - "
                f"{df.loc[df['id'] == sid, 'name'].iloc[0]}"
            )
        )

        student = df[df["id"] == selected_id].iloc[0]

        with st.form("edit_form"):
            roll = st.text_input(
                "Roll Number", value=student["roll_no"]
            )
            name = st.text_input(
                "Full Name", value=student["name"]
            )

            courses = [
                "Python", "Artificial Intelligence",
                "Web Development", "Cybersecurity"
            ]

            course_index = (
                courses.index(student["course"])
                if student["course"] in courses else 0
            )

            course = st.selectbox(
                "Course", courses, index=course_index
            )
            age = st.number_input(
                "Age", 5, 100, int(student["age"])
            )
            marks = st.number_input(
                "Marks", 0.0, 100.0,
                float(student["marks"])
            )

            submitted = st.form_submit_button("Update Student")

        if submitted:
            if not roll.strip() or not name.strip():
                st.error("Roll number and name are required.")
            else:
                try:
                    update_student(
                        int(selected_id), roll.strip(),
                        name.strip(), course, age, marks
                    )
                    st.success("Student updated successfully!")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("That roll number is already in use.")


# ---------- DELETE STUDENT ----------
elif page == "Delete Student":
    st.title("🗑️ Delete Student")

    df = get_students()

    if df.empty:
        st.info("No student records to delete.")
    else:
        selected_id = st.selectbox(
            "Select Student ID",
            df["id"].tolist(),
            format_func=lambda sid: (
                f"{df.loc[df['id'] == sid, 'roll_no'].iloc[0]} - "
                f"{df.loc[df['id'] == sid, 'name'].iloc[0]}"
            )
        )

        student = df[df["id"] == selected_id].iloc[0]

        st.warning(
            f"Selected: {student['name']} "
            f"(Roll No: {student['roll_no']})"
        )

        confirm = st.checkbox(
            "I confirm that I want to delete this student."
        )

        if st.button("Delete Student", type="primary"):
            if confirm:
                delete_student(int(selected_id))
                st.success("Student deleted.")
                st.rerun()
            else:
                st.error("Please confirm before deleting.")
