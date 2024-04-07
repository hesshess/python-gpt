from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
import json
import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain.callbacks import StreamingStdOutCallbackHandler

function = {
    "name": "create_quiz",
    "description": "function that takes a list of questions and answers and returns a quiz",
    "parameters": {
        "type": "object",
        "properties": {
            "questions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "question": {
                            "type": "string",
                        },
                        "answers": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "answer": {
                                        "type": "string",
                                    },
                                    "correct": {
                                        "type": "boolean",
                                    },
                                },
                                "required": ["answer", "correct"],
                            },
                        },
                    },
                    "required": ["question", "answers"],
                },
            }
        },
        "required": ["questions"],
    },
}

st.set_page_config(
    page_title="QuizGPT",
    page_icon="⍰"
)
st.title("QuizGPT")

key = st.sidebar.text_input("⬇️ OPENAI API KEY 🔑")

if key:
    st.session_state['key'] = key
    llm = ChatOpenAI(
            temperature=0.1,
            model ="gpt-3.5-turbo-0125",
            streaming=True,
            openai_api_key=st.session_state['key'],
            callbacks=[
                StreamingStdOutCallbackHandler()
            ]
        ).bind(
            function_call={
                "name": "create_quiz",
            },
            functions=[
                function,
            ],
        )
    prompt = PromptTemplate.from_template("Make a {level} quiz about {term}")
    @st.cache_data(show_spinner="Making quiz...")
    def run_quiz_chain(topic, level):
        chain = prompt | llm
        return chain.invoke({'term': topic, 'level':level})
    docs= None
    level = st.sidebar.selectbox("Choose quiz difficulty you want",("Hard", "Easy"))
    topic = st.sidebar.text_input("Make quiz about...")
    if topic and level:
        response = run_quiz_chain(topic,level)
        docs = response.additional_kwargs["function_call"]["arguments"]      
        if docs:      
            response = json.loads(docs)
            st.sidebar.write(response)
            with st.form(key="questions_form", clear_on_submit=True):
                right_num = 0
                for question in response['questions']:
                    st.write(question['question'])
                    value = st.radio("Select an option", [answer["answer"] for answer in question['answers']], index=None)
                    real = ''
                    if {'answer': value, 'correct':True} in question['answers']:
                        right_num += 1
                button = st.form_submit_button()
            if button:
                if right_num == len(response['questions']):
                    st.balloons()
                else:
                    st.error(f"Your Score : {right_num}/{len(response['questions'])}")
else: 
    st.markdown(
    """
    Welcome to QuizGPT.
    
    I will make a quiz to test your knowlege and  help you study.
    
    ### ⬅️ Enter your OPENAI API KEY on the sidebar first🔑
    """)   


                # st.write(f"Your score is {right_num}/{len(response['questions'])}")
                # retake_btn = st.button("Retake")
    

