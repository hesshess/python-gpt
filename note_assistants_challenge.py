import time
import openai
import streamlit as st
import json
from langchain.utilities import DuckDuckGoSearchAPIWrapper
from langchain.tools import DuckDuckGoSearchResults
from langchain.retrievers import WikipediaRetriever
from langchain.document_loaders import AsyncChromiumLoader
from langchain.document_transformers import Html2TextTransformer


import nest_asyncio

nest_asyncio.apply()


def send_conversation(message, role, save=True):
    with st.chat_message(role):
        st.markdown(message)
    if save:
        st.session_state["messages"].append({"message": message, "role": role})


def paint_history():
    for message in st.session_state["messages"]:
        send_conversation(
            message["message"],
            message["role"],
            save=False,
        )


st.set_page_config(
    page_title="ASSISTANTS API",
    page_icon="🧞‍♂️",
)
st.markdown(
    """
    # OpenAI Assistants (Graduation Project)
"""
)

st.sidebar.link_button(
    "🏠 Github repository 🏠",
    "https://github.com/hesshess/python-gpt/blob/main/note_assistants_challenge.py",
)


def get_run(run_id, thread_id):
    return client.beta.threads.runs.retrieve(
        run_id=run_id,
        thread_id=thread_id,
    )


def send_message(thread_id, content):
    return client.beta.threads.messages.create(
        thread_id=thread_id, role="user", content=content
    )


def get_messages(thread_id):
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    messages = list(messages)
    messages.reverse()
    for message in messages:
        print(f"{message.role}: {message.content[0].text.value}")


def get_tool_outputs(run_id, thread_id):
    run = get_run(run_id, thread_id)
    outputs = []
    for action in run.required_action.submit_tool_outputs.tool_calls:
        action_id = action.id
        function = action.function
        print(f"❤️Calling function: {function.name} with arg {function.arguments}✅")
        args = function.arguments
        outputs.append(
            {
                "output": functions_map[function.name](json.loads(args)),
                "tool_call_id": action_id,
            }
        )
        print(outputs)

    return outputs


def submit_tool_outputs(run_id, thread_id):
    outpus = get_tool_outputs(run_id, thread_id)
    return client.beta.threads.runs.submit_tool_outputs(
        run_id=run_id,
        thread_id=thread_id,
        tool_outputs=outpus,
    )


def get_duckDuckGoSearch(inputs):
    query = inputs["query"]
    wrapper = DuckDuckGoSearchAPIWrapper(max_results=1)
    search = DuckDuckGoSearchResults(api_wrapper=wrapper)
    return search.run(query)


def get_wikipediaSearch(inputs):
    query = inputs["query"]
    retriever = WikipediaRetriever(top_k_results=1)
    docs = retriever.get_relevant_documents(query)
    html2text = Html2TextTransformer()
    docs_transformed = html2text.transform_documents(docs)
    return docs_transformed[0].page_content


def get_linkScrape(inputs):
    link = inputs["link"]
    lst = []
    lst.append(link)
    loader = AsyncChromiumLoader(lst)
    docs = loader.load()
    html2text = Html2TextTransformer()
    docs_transformed = html2text.transform_documents(docs)
    return docs_transformed[0].page_content


def saveTXTfileTool(inputs):
    doc = inputs["doc"]
    file_path = f"./files/{time.strftime('%H%M%S')}.txt"
    with open(file_path, "w") as f:
        f.write(doc)
    with open(file_path, "rb") as f2:
        btn = st.download_button(
            key=time.strftime("%H%M%S"),
            label="Download txt",
            data=f2,
            file_name="research.txt",
        )
    return doc


functions_map = {
    "get_duckDuckGoSearch": get_duckDuckGoSearch,
    "get_wikipediaSearch": get_wikipediaSearch,
    "get_linkScrape": get_linkScrape,
    "saveTXTfileTool": saveTXTfileTool,
}

functions = [
    {
        "type": "function",
        "function": {
            "name": "get_wikipediaSearch",
            "description": "Use this tool to research.It takes a query as an argument and return content",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The query you will search for.",
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_duckDuckGoSearch",
            "description": "Use this tool to find the ONLY ONE link to the most relevant result for my research.It takes a query as an argument and you return ONE link.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The query you will search for.",
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_linkScrape",
            "description": "You have the one website link from DuckDuckGo,Use this to get the content of the link for my research. You shoud enter the ONLY ONE link and return the content",
            "parameters": {
                "type": "object",
                "properties": {
                    "link": {
                        "type": "string",
                        "description": "The ONE link you will extract it's content. Example: 'https://www.wired.com/story/xz-backdoor-everything-you-need-to-know/'",
                    },
                },
                "required": ["link"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "saveTXTfileTool",
            "description": "If you found the website link in DuckDuckGo and extracted the content or Wikipedia content, Use this to save the content to a .txt file for my research.You shoud enter long text that you extracted from the websites.",
            "parameters": {
                "type": "object",
                "properties": {
                    "doc": {
                        "type": "string",
                        "description": "the content extracted from the link and you will save to .txt file.",
                    },
                },
                "required": ["doc"],
            },
        },
    },
]


@st.cache_resource(show_spinner="Creating Assistant...")
def create_assistant(name):
    assistant = client.beta.assistants.create(
        name=name,
        instructions="You help users do research in Wikipedia and DuckDuckGo. when you find the website link from DuckDuckGo and extract the content of the link and you save the content to a .txt file for my research. Don't forget to save the .txt file",
        model="gpt-4-1106-preview",
        tools=functions,
    )
    st.session_state["assistant_id"] = assistant.id
    return st.session_state.assistant_id


@st.cache_resource(show_spinner="Creating Thread...")
def create_thread(query):
    thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": query,
            }
        ]
    )
    st.session_state["thread_id"] = thread.id
    return st.session_state.thread_id


@st.cache_resource(show_spinner="Creating Run...")
def create_run(thread_id, assistant_id):
    print(f"{thread_id}🥳🥶{assistant_id}")
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id,
    )
    st.session_state["run_id"] = run.id
    return st.session_state.run_id


key = st.sidebar.text_input("⬇️ OPENAI API KEY 🔑")

if key:
    st.session_state["key"] = key
    client = openai.Client(api_key=st.session_state["key"])
    assistant_id = create_assistant("Research-7")
    if assistant_id:
        send_conversation("I'm ready! Let's research!", "ai", save=False)
        paint_history()
        query = st.chat_input("What do you want to research about...？")
        if query is not None:
            send_conversation(query, "human")
            with st.status("Starting work...", expanded=False) as status_box:
                thread_id = create_thread(query)
                run_id = create_run(thread_id, assistant_id)
                run = get_run(run_id, thread_id)
                while run.status != "completed":
                    status_box.update(label=f"{run.status}...", state="running")
                    if run.status == "requires_action":
                        submit_tool_outputs(run_id, thread_id)
                    run = get_run(
                        run_id,
                        thread_id,
                    )
                status_box.update(label="Complete", state="complete", expanded=True)
                messages = client.beta.threads.messages.list(thread_id=thread_id)
                send_conversation(messages.data[0].content[0].text.value, "ai")
else:
    st.session_state["messages"] = []
    st.session_state["key"] = []
    st.session_state["assistant_id"] = []
    st.session_state["thread_id"] = []
    st.session_state["run_id"] = []
