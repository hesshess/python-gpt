
        
import time
import streamlit as st

st.set_page_config(
    page_title="DocumentGPT",
    page_icon="📃"
)

st.title("Document GPT")

# with st.chat_message("human"):
#     st.write("Hello")
# with st.chat_message("ai"):
#     st.write("how are you?")

# with st.status("Embedding file...", expanded=True) as status:
#     time.sleep(2)
#     st.write("Getting the file")
#     time.sleep(2)
#     st.write("Embedding the file")
#     time.sleep(2)
#     st.write("Caching the file")
#     status.update(label="Error", state="error")

def send_message(message,role, save=True):
    with st.chat_message(role):
        st.write(message)
        if save:
            st.session_state['messages'].append({"message": message, "role": role})

if "messages" not in st.session_state:
    st.session_state['messages']=[]
    

for message in st.session_state['messages']:
    send_message(message['message'], message['role'], save=False)
    

message = st.chat_input("send a message to ai")

if message:
    send_message(message, "human")
    time.sleep(2)
    send_message(f"Yousaid: {message}", "ai")
