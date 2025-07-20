import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.llms import Ollama

# === Prompt Template ===
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Please respond to user queries."),
    ("user", "Question: {question}")
])

# === Page Config ===
st.set_page_config(page_title="Chatbox - Gemma3:1b", layout="wide")


st.markdown("""
<style>
.block-container {
    padding-top: 0rem;
}

/* Outer wrapper for message rows */
.message-row {
    display: flex;
    width: 100%;
    margin-top: 0.3rem;
}

/* User message row aligns to right */
.user-row {
    justify-content: flex-end;
}

/* Bot message row aligns to left */
.bot-row {
    justify-content: flex-start;
}

.user-msg {
    background-color: #0B7285; /* Teal */
    color: white;
    padding: 10px 14px;
    border-radius: 16px;
    max-width: 75%;
}

.bot-msg {
    background-color: #3E3E3E; /* Soft dark gray */
    color: white;
    padding: 10px 14px;
    border-radius: 16px;
    max-width: 75%;
}

.chat-container {
    padding: 0 0.5rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    margin-top: 1rem;
}
</style>
""", unsafe_allow_html=True)


# === CSS ===
# st.markdown("""
# <style>
# .block-container {
#     padding-top: 0rem;
# }

# .chat-container {
#     background-color: transparent;
#     padding: 0 0.5rem;
#     display: flex;
#     flex-direction: column;
#     gap: 0.5rem;
#     margin-top: 1rem;
# }

# .user-msg {
#     align-self: flex-end;
#     background-color: #2e7d32;
#     color: white;
#     padding: 10px 14px;
#     border-radius: 16px;
#     max-width: 75%;
# }

# .bot-msg {
#     align-self: flex-start;
#     background-color: #424242;
#     color: white;
#     padding: 10px 14px;
#     border-radius: 16px;
#     max-width: 75%;
# }
# </style>
# """, unsafe_allow_html=True)

# === Init Chat State ===
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "user_input" not in st.session_state:
    st.session_state.user_input = ""
print("*"*100)

# === Input Handler ===
def handle_input():
    print("-"*100)
    print("inside handle input")
    input_text = st.session_state.user_input.strip()
    if not input_text:
        return

    st.session_state.chat_history.append({"role": "user", "message": input_text})

    llm = Ollama(model="gemma3:1b")
    output_parser = StrOutputParser()
    chain = prompt | llm | output_parser
    response = chain.invoke({"question": input_text})
    print(f"{input_text= },{response= }")
    st.session_state.chat_history.append({"role": "bot", "message": response})
    st.session_state.user_input = ""  # Clear input

# === Layout ===
col1, col2 = st.columns([1, 3])

# === Left: History ===
with col1:
    print("entery A")
    st.title("History")
    if st.session_state.chat_history:
        for msg in st.session_state.chat_history:
            who = "You" if msg["role"] == "user" else "Gemma"
            st.markdown(f"- **{who}:** {msg['message']}")
    else:
        pass
        #st.info("No history yet.")

# === Right: Chat UI ===
with col2:
    print("entery B")
    st.title("Chat with Gemma3:1b")

    with st.container():
        st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
        print(f"{st.session_state.chat_history= }")
        for msg in st.session_state.chat_history:
            role = msg["role"]
            row_class = "user-row" if role == "user" else "bot-row"
            msg_class = "user-msg" if role == "user" else "bot-msg"
            st.markdown(
                f"<div class='message-row {row_class}'>"
                f"<div class='{msg_class}'>{msg['message']}</div>"
                f"</div>",
                unsafe_allow_html=True
            )
        st.markdown("</div>", unsafe_allow_html=True)

    # ✅ Unique key avoids the DuplicateElementKey error
    st.text_input("Ask me a question...", key="user_input", on_change=handle_input)

