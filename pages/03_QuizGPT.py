import streamlit as st
from langchain.retrievers import WikipediaRetriever
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
from langchain.memory import ConversationSummaryBufferMemory


st.set_page_config(
    page_title="QuizGPT",
    page_icon="⍰"
)
st.title("QuizGPT")

@st.cache_data(show_spinner="Embedding file...")
def embed_file(file):
    file_content = file.read()
    file_path = f"./.cache/files/{file.name}"
    with open(file_path, 'wb') as f:
        f.write(file_content)
    cache_dir = LocalFileStore(f"./.cache/embeddings/{file.name}") 
    splitter = CharacterTextSplitter.from_tiktoken_encoder(
        separator="\n",
        chunk_size=600,
        chunk_overlap=100,
    )   
    loader = UnstructuredFileLoader(file_path)
    docs = loader.load_and_split(text_splitter=splitter)

with st.sidebar:
    choice = st.selectbox("Choose what you want to use.",("File", "Wikipedia Article"))
    if choice == "File":
        file = st.file_uploader("Upload a .dox, .txt for .pdf file", type=["pdf", "txt", "docx"])
    else:
        topic = st.text_input("Search Wikipedia...")
        if topic:
            retriever = WikipediaRetriever(top_k_results=1)
            with st.status("Searching Wikipedia..."):
                docs = retriever.get_relevant_documents(topic)
                