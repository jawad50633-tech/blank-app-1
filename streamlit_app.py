
import streamlit as st


st.header("Welcome to Python Class")
st.subheader("My first Streamlit project")

st.table({
    "Name": ["Alice", "Bob", "Charlie"],
    "Age": [25, 30, 35],
    "marks": [85, 90, 95]
    })

st.divider()

st.code("print('Hello World')", language="python")
