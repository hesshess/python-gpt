import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="Fullstack GPT Home",
    page_icon="🤖",
)
st.title("Fullstack GPT Home")

today = datetime.today().strftime("%H:%M:%S")
st.title(today)
model = st.selectbox("Choose your model", ("GPT-3", "GPT-4",))
if model == "GPT-3":
    st.write("cheap")
else:
    st.write("not cheap")
name = st.text_input("what is your name?")
st.write(name)
value = st.slider("temperature", min_value=0.1, max_value=1.0)
st.write(value)

with st.sidebar:
    st.title("sidebar title")
    st.text_input("asdf")
    
tab_one, tab_two, tab_three = st.tabs(['A','B','C'])
with tab_one:
    st.write('one')
with tab_two:
    st.write('two')
with tab_three:
    st.write('three')
                                       