import streamlit as st
import requests
import uuid

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="ChatBot Prototype",
    page_icon="🤖",
    layout="centered"
)

# --- CUSTOM CSS FOR FONTS ---
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Zalando+Sans+Expanded:ital,wght@0,200..900;1,200..900&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=TikTok+Sans:opsz,wght@12..36,300..900&display=swap" rel="stylesheet">

<style>
    /* Apply Zalando Sans Expanded to title and subtitle only */
    h1, .subtitle {
        font-family: "Zalando Sans Expanded", sans-serif !important;
        text-align: center !important;
    }
    
    /* Center the subtitle text */
    .subtitle {
        text-align: center !important;
        margin-bottom: 2rem !important;
    }
    
    /* Apply TikTok Sans to chat messages */
    .stChatMessage {
        font-family: "TikTok Sans", sans-serif !important;
    }
    
    /* --- BUTTON FONT FIX (NUCLEAR OPTION) --- */
    
    /* Target "Reset Session" (Standard Button) AND all its children elements */
    div[data-testid="stButton"] button, 
    div[data-testid="stButton"] button * {
        font-family: "Zalando Sans Expanded", sans-serif !important;
        font-weight: 600 !important;
    }
    
    /* Target "Launch" (Link Button) AND all its children elements */
    div[data-testid="stLinkButton"] a, 
    div[data-testid="stLinkButton"] a * {
        font-family: "Zalando Sans Expanded", sans-serif !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# --- BACKEND API DETAILS ---
try:
    API_URL = st.secrets["api"]["url"]
    API_KEY = st.secrets["api"]["key"]
except KeyError:
    API_URL = "http://localhost:8000" 
    API_KEY = "test"

# --- UI & LOGIC ---
st.title("WhatsApp Chat Bot 2.0 Prototype 🤖")
st.markdown('<p class="subtitle">I am a Relai Expert real-estate AI Agent ready to help you find your ideal property.</p>', unsafe_allow_html=True)

# --- LAYOUT: CENTERED BUTTONS ---
# Using columns to center the buttons perfectly
col_spacer1, col_btn1, col_btn2, col_spacer2 = st.columns([1, 2, 2, 1])

with col_btn1:
    st.link_button(
        "Launch 🚀", 
        "https://api.whatsapp.com/send/?phone=917331112955&text=Hi%21+I+need+help+with+property+recommendations.&type=phone_number&app_absent=0",
        use_container_width=True
    )

with col_btn2:
    if st.button("Reset Session 🔄", use_container_width=True):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

# --- CHAT INTERFACE ---
st.divider()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("How can I help you today?"):
    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.messages.append({"role": "user", "content": prompt})

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

            response = requests.get(API_URL, headers=headers, json=payload, timeout=120)
            response.raise_for_status()

            backend_response = response.json()
            assistant_reply = backend_response.get("reply", "Sorry, I encountered an error.")

            with st.chat_message("assistant"):
                st.markdown(assistant_reply)

            st.session_state.messages.append({"role": "assistant", "content": assistant_reply})

        except requests.exceptions.RequestException as e:
            st.error(f"Could not connect to the AI agent. Please try again later.")
