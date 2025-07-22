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

/* History styling */
.chat-item {
    background-color: #f0f2f6;
    padding: 8px 12px;
    margin: 4px 0;
    border-radius: 8px;
    cursor: pointer;
    transition: background-color 0.2s;
}

.chat-item:hover {
    background-color: #e8eaed;
}

.chat-item.active {
    background-color: #0B7285;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# === Init Chat State ===
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = []  # List of chat sessions
if "current_chat_index" not in st.session_state:
    st.session_state.current_chat_index = -1  # No active chat initially
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

    # Create new chat session if none exists or starting fresh
    if st.session_state.current_chat_index == -1:
        new_chat = {
            "id": len(st.session_state.chat_sessions) + 1,
            "messages": [],
            "title": f"Chat {len(st.session_state.chat_sessions) + 1}",
            "first_question": input_text[:30] + "..." if len(input_text) > 30 else input_text
        }
        st.session_state.chat_sessions.append(new_chat)
        st.session_state.current_chat_index = len(st.session_state.chat_sessions) - 1

    # Add user message to current chat
    current_chat = st.session_state.chat_sessions[st.session_state.current_chat_index]
    current_chat["messages"].append({"role": "user", "message": input_text})

    # Get bot response
    llm = Ollama(model="gemma3:1b")
    output_parser = StrOutputParser()
    chain = prompt | llm | output_parser
    response = chain.invoke({"question": input_text})
    print(f"{input_text= },{response= }")
    
    # Add bot response to current chat
    current_chat["messages"].append({"role": "bot", "message": response})
    st.session_state.user_input = ""  # Clear input

def start_new_chat():
    """Start a new chat session"""
    st.session_state.current_chat_index = -1

def select_chat(chat_index):
    """Select a specific chat session"""
    st.session_state.current_chat_index = chat_index

def delete_chat(chat_index):
    """Delete a specific chat session"""
    if len(st.session_state.chat_sessions) > chat_index:
        del st.session_state.chat_sessions[chat_index]
        # Adjust current chat index if necessary
        if st.session_state.current_chat_index == chat_index:
            st.session_state.current_chat_index = -1
        elif st.session_state.current_chat_index > chat_index:
            st.session_state.current_chat_index -= 1

# === Layout ===
col1, col2 = st.columns([1, 3])

# === Left: History ===
with col1:
    print("entry A")
    print(f"{st.session_state.current_chat_index= }")
    # Header with New Chat button
    col_title, col_btn = st.columns([2, 1])
    with col_title:
        st.title("History")
    with col_btn:
        print("entry A.2")
        if st.button("New Chat", key="new_chat"):
            start_new_chat()
    
    # Display chat sessions
    if st.session_state.chat_sessions:
        for i, chat_session in enumerate(st.session_state.chat_sessions):
            col_chat, col_del = st.columns([4, 1])
            
            with col_chat:
                is_active = i == st.session_state.current_chat_index
                button_style = "🔵" if is_active else "⚫"
                
                if st.button(
                    f"{button_style} {chat_session['title']}", 
                    key=f"chat_{i}",
                    help=chat_session['first_question']
                ):
                    select_chat(i)
            
            with col_del:
                if st.button("🗑️", key=f"delete_{i}", help="Delete chat"):
                    delete_chat(i)
                    st.rerun()
    else:
        #st.info("No chat history yet.")
        print("no chat history yet")
        pass

# === Right: Chat UI ===
with col2:
    print("entry B")
    print(f"{st.session_state.current_chat_index= }")
    # Display current chat title
    if st.session_state.current_chat_index >= 0:
        current_chat = st.session_state.chat_sessions[st.session_state.current_chat_index]
        st.title(f"Chat with Gemma3:1b - {current_chat['title']}")
        messages_to_display = current_chat["messages"]
    else:
        st.title("Chat with Gemma3:1b - New Chat")
        messages_to_display = []

    # Chat messages container
    with st.container():
        st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
        print(f"messages_to_display= {messages_to_display}")
        
        for msg in messages_to_display:
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

    # Input field
    st.text_input("Ask me a question...", key="user_input", on_change=handle_input)
