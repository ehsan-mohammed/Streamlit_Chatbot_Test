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
<link href="https://fonts.googleapis.com/css2?family=Recursive:wght@300..1000&display=swap" rel="stylesheet">

<style>
    /* 1. HEADERS & SUBTITLES (Zalando) */
    h1, .subtitle {
        font-family: "Zalando Sans Expanded", sans-serif !important;
        text-align: center !important;
    }
    
    .subtitle {
        margin-bottom: 2rem !important;
    }

    /* 2. BUTTONS (Zalando) */
    /* Target "Reset" button text */
    div[data-testid="stButton"] button, 
    div[data-testid="stButton"] button * {
        font-family: "Zalando Sans Expanded", sans-serif !important;
        font-weight: 600 !important;
    }
    
    /* Target "Launch" link button text */
    div[data-testid="stLinkButton"] a, 
    div[data-testid="stLinkButton"] a * {
        font-family: "Zalando Sans Expanded", sans-serif !important;
        font-weight: 600 !important;
    }

    /* 3. CHAT MESSAGES (Recursive) */
    /* Target the markdown container INSIDE the chat message */
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] * {
        font-family: "Recursive", sans-serif !important;
    }
    
    /* Apply to the container wrapper as well for good measure */
    [data-testid="stChatMessage"] {
        font-family: "Recursive", sans-serif !important;
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
col_spacer1, col_btn1, col_btn2, col_spacer2 = st.columns([1, 2, 2, 1])

with col_btn1:
    st.link_button(
        "Launch 🚀", 
        "https://api.whatsapp.com/send/?phone=917331112955&text=Hi%21+I+need+help+with+property+recommendations.&type=phone_number&app_absent=0",
        use_container_width=True
    )

with col_btn2:
    if st.button("Reset 🔄", use_container_width=True):
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
