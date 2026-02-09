import time
import uuid
import requests
import streamlit as st

# --- CONFIGURATION & CONSTANTS ---
PAGE_TITLE = "ChatBot Prototype"
PAGE_ICON = "🤖"
COOLDOWN_SECONDS = 3.0  # Time in seconds between allowed API calls
API_TIMEOUT = 120       # Timeout for backend requests

st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout="centered"
)

# --- CUSTOM CSS ---
# Imports fonts and overrides default Streamlit styles for specific branding
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Zalando+Sans+Expanded:ital,wght@0,200..900;1,200..900&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Recursive:wght@300..1000&display=swap" rel="stylesheet">

<style>
    /* 1. Global Font Overrides */
    h1, .subtitle {
        font-family: "Zalando Sans Expanded", sans-serif !important;
        text-align: center !important;
    }
    .subtitle {
        margin-bottom: 2rem !important;
    }

    /* 2. Button Styling */
    div[data-testid="stButton"] button, 
    div[data-testid="stButton"] button *,
    div[data-testid="stLinkButton"] a, 
    div[data-testid="stLinkButton"] a * {
        font-family: "Zalando Sans Expanded", sans-serif !important;
        font-weight: 600 !important;
    }

    /* 3. Chat Message Styling */
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] *,
    [data-testid="stChatMessage"] {
        font-family: "Recursive", sans-serif !important;
    }

    /* 4. Avatar Fix (Force default emoji font for cleaner look) */
    [data-testid="stChatAvatar"] {
        font-family: sans-serif, "Segoe UI Emoji", "Apple Color Emoji" !important;
    }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE MANAGEMENT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Track the timestamp of the last successful API call for rate limiting
if "last_api_call_time" not in st.session_state:
    st.session_state.last_api_call_time = 0

# --- API CREDENTIALS ---
try:
    API_URL = st.secrets["api"]["url"]
    API_KEY = st.secrets["api"]["key"]
except (KeyError, FileNotFoundError):
    # Fallback for local development if secrets.toml is missing
    API_URL = "http://localhost:8000"
    API_KEY = "dev_mode"

# --- UI HEADER ---
# HTML allows us to bypass specific Streamlit font styles for the title
st.markdown("<h1 style='text-align: center;'>WhatsApp Chat Bot 2.0 Prototype</h1>", unsafe_allow_html=True)
st.markdown('<p class="subtitle">I am a Relai Expert real-estate AI Agent ready to help you find your ideal property.</p>', unsafe_allow_html=True)

# --- ACTION BUTTONS ---
col_spacer1, col_btn1, col_btn2, col_spacer2 = st.columns([1, 2, 2, 1])

with col_btn1:
    st.link_button(
        "Launch 🚀", 
        "https://api.whatsapp.com/send/?phone=917331112955&text=Hi&type=phone_number&app_absent=0",
        use_container_width=True
    )

with col_btn2:
    if st.button("Reset 🔄", use_container_width=True):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.last_api_call_time = 0
        st.rerun()

# --- CHAT INTERFACE ---
st.divider()

# Display historical messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle new user input
if prompt := st.chat_input("How can I help you today?"):
    
    # 1. Rate Limiting Check
    current_time = time.time()
    time_since_last_call = current_time - st.session_state.last_api_call_time
    
    # Render user message immediately for responsiveness
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Block request if within cooldown period
    if time_since_last_call < COOLDOWN_SECONDS:
        st.warning(f"⚠️ You are sending messages too quickly. Please wait {int(COOLDOWN_SECONDS)} seconds.")
        st.stop() # Halts execution here; no API call is made

    # 2. API Interaction
    st.session_state.last_api_call_time = current_time # Update timestamp start
    
    with st.spinner("Thinking..."):
        try:
            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "message": prompt,
                "sessionId": st.session_state.session_id
            }

            response = requests.get(API_URL, headers=headers, json=payload, timeout=API_TIMEOUT)
            response.raise_for_status()

            backend_response = response.json()
            assistant_reply = backend_response.get("reply", "I'm sorry, I couldn't generate a response.")

            with st.chat_message("assistant"):
                st.markdown(assistant_reply)

            st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
            
            # Reset timer after successful response to prevent immediate follow-up spam
            st.session_state.last_api_call_time = time.time()

        except requests.exceptions.RequestException as e:
            st.error("Could not connect to the AI agent. Please try again later.")
            # Optional: Log the specific error to console for debugging
            print(f"API Error: {e}")
