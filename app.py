import time
import uuid
import requests
import streamlit as st

# --- CONFIGURATION ---
PAGE_TITLE = "ChatBot Prototype"
PAGE_ICON = "🤖"
API_TIMEOUT = 120 

st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout="centered"
)

# --- CUSTOM CSS ---
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Zalando+Sans+Expanded:ital,wght@0,200..900;1,200..900&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Recursive:wght@300..1000&display=swap" rel="stylesheet">

<style>
    /* [Your existing CSS remains exactly the same] */
    h1, .subtitle { font-family: "Zalando Sans Expanded", sans-serif !important; text-align: center !important; }
    .subtitle { margin-bottom: 2rem !important; }
    div[data-testid="stButton"] button, div[data-testid="stButton"] button *, div[data-testid="stLinkButton"] a, div[data-testid="stLinkButton"] a * { font-family: "Zalando Sans Expanded", sans-serif !important; font-weight: 600 !important; }
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] *, [data-testid="stChatMessage"] { font-family: "Recursive", sans-serif !important; }
    [data-testid="stChatAvatar"] { font-family: sans-serif, "Segoe UI Emoji", "Apple Color Emoji" !important; }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# [NEW] State to track if we are currently waiting for an answer
if "processing" not in st.session_state:
    st.session_state.processing = False

# --- API CONFIG ---
try:
    API_URL = st.secrets["api"]["url"]
    API_KEY = st.secrets["api"]["key"]
except (KeyError, FileNotFoundError):
    API_URL = "http://localhost:8000"
    API_KEY = "dev_mode"

# --- HELPER FUNCTIONS ---
def lock_input():
    """Callback to lock the UI immediately when user hits Enter."""
    st.session_state.processing = True

# --- UI HEADER ---
st.markdown("<h1 style='text-align: center;'>WhatsApp Chat Bot 2.0 Prototype</h1>", unsafe_allow_html=True)
st.markdown('<p class="subtitle">I am a Relai Expert real-estate AI Agent ready to help you find your ideal property.</p>', unsafe_allow_html=True)

# --- ACTION BUTTONS ---
col_spacer1, col_btn1, col_btn2, col_spacer2 = st.columns([1, 2, 2, 1])

with col_btn1:
    st.link_button("Launch 🚀", "https://api.whatsapp.com/send/?phone=917331112955&text=Hi", use_container_width=True)

with col_btn2:
    if st.button("Reset 🔄", use_container_width=True):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.processing = False # Ensure we unlock on reset
        st.rerun()

st.divider()

# --- CHAT HISTORY ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- CHAT INPUT & LOGIC ---

# 1. The Input Widget
# We bind the 'disabled' state to our session variable.
# We use 'on_submit' to trigger the lock BEFORE the script re-runs.
prompt = st.chat_input(
    "How can I help you today?", 
    disabled=st.session_state.processing, 
    on_submit=lock_input
)

if prompt:
    # 2. Render User Message
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 3. API Call
    with st.spinner("Thinking..."):
        try:
            headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
            payload = {"message": prompt, "sessionId": st.session_state.session_id}
            
            # This call blocks the script while it waits
            response = requests.get(API_URL, headers=headers, json=payload, timeout=API_TIMEOUT)
            response.raise_for_status()
            
            assistant_reply = response.json().get("reply", "I'm sorry, I couldn't generate a response.")

            with st.chat_message("assistant"):
                st.markdown(assistant_reply)
            st.session_state.messages.append({"role": "assistant", "content": assistant_reply})

        except requests.exceptions.RequestException as e:
            st.error("Could not connect to the AI agent. Please try again later.")
        
        finally:
            # 4. UNLOCK & RERUN
            # We must set processing to False and immediately rerun to reactivate the input box
            st.session_state.processing = False
            st.rerun()
