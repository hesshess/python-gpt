import os
from langchain.callbacks.base import BaseCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import UnstructuredFileLoader
from langchain.schema.output import ChatGenerationChunk, GenerationChunk
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings, CacheBackedEmbeddings
from langchain.vectorstores import FAISS
from langchain.storage import LocalFileStore
from langchain.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain.schema.runnable import RunnablePassthrough, RunnableLambda
from langchain.memory import ConversationBufferMemory

import time
import streamlit as st

st.set_page_config(
    page_title="DocumentGPT",
    page_icon="📃"
)
st.title("Document GPT")

st.markdown("""
            Welcome! Use this chatbot to ask questions to an AI about your files!
            
           ### ⬅️ Enter your OPENAI API KEY on the sidebar first🔑
       
            """)

def save_message(message, role):
    st.session_state['messages'].append({'role': role, 'message': message})

@st.cache_data(show_spinner="Embedding file...")
def embed_file(file):
    file_content = file.read()
    file_path = f"./files/{file.name}"
    os.makedirs(file_path, mode=0o777, exist_ok=True)
    with open(file_path, 'wb') as f:
        f.write(file_content)
    os.makedirs(f"./embeddings/{file.name}", mode=0o777, exist_ok=True)
    cache_dir = LocalFileStore(f"./embeddings/{file.name}")
    splitter = CharacterTextSplitter.from_tiktoken_encoder(
        separator="\n",
        chunk_size=600,
        chunk_overlap=100,
    )   
    loader = UnstructuredFileLoader(file_path)
    docs = loader.load_and_split(text_splitter=splitter)
    embeddings = OpenAIEmbeddings(openai_api_key=st.session_state.key) 
    cached_embeddings = CacheBackedEmbeddings.from_bytes_store(
        embeddings, cache_dir
    )   
    vectorstore = FAISS.from_documents(docs,    cached_embeddings) 
    retriever = vectorstore.as_retriever()
    return retriever



def send_message(message, role, save=True):
    with st.chat_message(role):
        st.markdown(message)
    if save:
        save_message(message, role)

def paint_history():
    for message in st.session_state['messages']:
        send_message(message['message'], message['role'], save=False) 
        
def format_docs(docs):
    return "\n\n".join(document.page_content for document in docs)

def load_memory(_):
    print(f"❌{memory.load_memory_variables({})}❌")
    return memory.load_memory_variables({})["chat_history"]

def invoke_chain(question):
    result = chain.invoke(question)
    memory.save_context({'input': question}, {'output': str(result.content)})
    print(f"👹{memory.load_memory_variables({})}👹")


class ChatCallBackHandler(BaseCallbackHandler):
    message = ''
    message_b = st.empty()
    def on_llm_start(self, *arg, **kwargs):
        self.message_b = st.empty()
    def on_llm_end(self, *arg, **kwargs):
         save_message(self.message, 'ai')
    def on_llm_new_token(self, token: str, *arg, **kwargs):
        self.message +=token
        self.message_b.markdown(self.message)



key = st.sidebar.text_input("⬇️ OPENAI API KEY 🔑")
        
if key:
    st.session_state['key'] = key
    llm = ChatOpenAI(
        temperature=0.1,
        streaming=True,
        callbacks=[
            ChatCallBackHandler(),
        ],
        openai_api_key=st.session_state.key,
    )
    memory = ConversationBufferMemory(
        memory_key='chat_history',
        return_messages=True,
    )
    print(f"🌞new ConversationBufferMemory💩")
    
    prompt = ChatPromptTemplate.from_messages([
    ('system', """
    Answer the question using ONLY the following context. If you don't know the answer, just say you don't know. Don't make anything up!
    
    Context: {context}
    """),
    MessagesPlaceholder(variable_name='chat_history'),
    ('human', '{question}')
])

    with st.sidebar:
        file = st.file_uploader(
        "Upload a .txt .pdf or .dcx file",
        type=["pdf", "txt", "docs"])
    
    if file:
        retriever = embed_file(file)
        send_message("I'm ready! Ask away!", "ai", save=False)
        paint_history()
        message = st.chat_input("Ask anything about your file...")   
        if message:
            send_message(message, "human")
            chain = ({
                'context': retriever | RunnableLambda(format_docs),
                'question': RunnablePassthrough(),
                'chat_history': RunnableLambda(load_memory)
            } | prompt | llm)
            with st.chat_message('ai'):
                response = invoke_chain(message) 
            
    else:
        st.session_state['messages'] = [] 
        del st.session_state['key']

st.sidebar.link_button("🏠 Github repository 🏠", 'https://github.com/hesshess/python-gpt')