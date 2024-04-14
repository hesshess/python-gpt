import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain.utilities.duckduckgo_search import DuckDuckGoSearchAPIWrapper
import yfinance
import json

import openai as client

st.set_page_config(
    page_title="ASSISTANTS API",
    page_icon="🧞‍♂️",
)
st.markdown(
    """
    # OpenAI Assistants (Graduation Project)
Refactor the agent you made in the previous assignment into an OpenAI Assistant.
Give it a user interface with Streamlit that displays the conversation history.
Allow the user to use its own OpenAI API Key, load it from an st.input inside of st.sidebar
Using st.sidebar put a link to the Github repo with the code of your Streamlit app.

"""
)


key = st.sidebar.text_input("⬇️ OPENAI API KEY 🔑")

if key:
    st.session_state["key"] = key
    llm = ChatOpenAI(temperature=0.1, api_key=st.session_state["key"])
    query = st.text_input("Ask a question to the website.")


st.sidebar.link_button(
    "🏠 Github repository 🏠",
    "https://github.com/hesshess/python-gpt/",
)
