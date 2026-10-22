
import streamlit as st

st.title("📊 Student Marks Calculator")

name = st.text_input("Student name")

maths = st.number_input("Maths marks", 0, 100, 0)
python = st.number_input("Python marks", 0, 100, 0)
english = st.number_input("English marks", 0, 100, 0)

if st.button("Calculate Result"):
    total = maths + python + english
    percentage = total / 300 * 100

    st.write("Student:", name)
    st.metric("Total Marks", f"{total}/300")
    st.metric("Percentage", f"{percentage:.1f}%")

    if percentage >= 80:
        st.success("Grade: A")
    elif percentage >= 60:
        st.info("Grade: B")
    elif percentage >= 40:
        st.warning("Grade: C")
    else:
        st.error("Grade: Fail")
