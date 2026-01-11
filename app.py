import streamlit as st
import requests
import uuid

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Relai Estate",
    page_icon="🏢",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CUSTOM CSS (The Design Logic) ---
st.markdown("""
<style>
    /* 1. IMPORT FONTS */
    @import url('https://fonts.googleapis.com/css2?family=Antonio:wght@100;700&family=Space+Grotesk:wght@300;400;600&display=swap');

    /* 2. GLOBAL OVERRIDES */
    .stApp {
        background-color: #050505; /* Deepest Black */
    }
    
    html, body, [class*="css"]  {
        font-family: 'Space Grotesk', sans-serif; /* Tech/Modern Body Font */
        color: #e0e0e0;
    }

    /* 3. TYPOGRAPHY STYLING */
    h1, h2, h3 {
        font-family: 'Antonio', sans-serif !important; /* The "Long" Font */
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: 700;
    }

    /* The Main Title Style */
    .hero-title {
        font-size: 4.5rem !important;
        background: linear-gradient(to right, #ffffff, #888888);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0px;
        line-height: 1.1;
    }

    .hero-subtitle {
        font-family: 'Space Grotesk', sans-serif;
        color: #00D26A; /* WhatsApp/Emerald Green */
        text-align: center;
        font-size: 1rem;
        letter-spacing: 1px;
        margin-bottom: 40px;
        text-transform: uppercase;
        opacity: 0.8;
    }

    /* 4. CHAT MESSAGE STYLING */
    /* Remove default backgrounds to make it look cleaner */
    .stChatMessage {
        background-color: transparent !important;
        border: none !important;
    }

    /* User Message */
    .stChatMessage[data-testid="stChatMessage"]:nth-child(odd) {
        border-left: 2px solid #333;
        padding-left: 15px;
    }
    
    /* Assistant Message */
    .stChatMessage[data-testid="stChatMessage"]:nth-child(even) {
        border-left: 2px solid #00D26A;
        padding-left: 15px;
        background: rgba(0, 210, 106, 0.05) !important; /* Slight green tint */
    }

    /* 5. INPUT FIELD STYLING */
    .stChatInput textarea {
        background-color: #111 !important;
        color: white !important;
        border: 1px solid #333 !important;
        border-radius: 0px !important; /* Square corners for pro look */
    }
    .stChatInput textarea:focus {
        border-color: #00D26A !important;
        box-shadow: 0 0 10px rgba(0, 210, 106, 0.2) !important;
    }

    /* 6. BUTTON / SUGGESTION STYLING */
    /* Making buttons look like architectural chips */
    div.stButton > button {
        width: 100%;
        background-color: transparent;
        color: #888;
        border: 1px solid #333;
        border-radius: 4px;
        padding: 15px 10px;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 0.9rem;
        transition: all 0.3s ease;
        text-align: left;
    }
    
    div.stButton > button:hover {
        border-color: #00D26A;
        color: #fff;
        background-color: rgba(0, 210, 106, 0.05);
        transform: translateX(5px); /* Slide effect */
    }

    /* Hide standard UI elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# --- BACKEND API SETUP ---
# Load secrets or use fallback for testing
try:
    API_URL = st.secrets["api"]["url"]
    API_KEY = st.secrets["api"]["key"]
except KeyError:
    API_URL = "http://localhost:3000/chat"
    API_KEY = "test"

# --- SIDEBAR (Controls) ---
with st.sidebar:
    st.markdown("### SYSTEM CONTROLS")
    if st.button("RESET MEMORY ⟳"):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()
    
    st.markdown("---")
    st.markdown("<div style='font-size:0.8rem; color:#666;'>RELAI ESTATE AGENT<br>V 2.0 BETA</div>", unsafe_allow_html=True)

# --- HERO SECTION ---
# Using HTML for the custom header look
st.markdown('<div class="hero-title">RELAI</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Real Estate Intelligence Unit</div>', unsafe_allow_html=True)

# --- CHAT HISTORY ---
# Display existing messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- EMPTY STATE (Suggestions) ---
# Only show these if chat history is empty
if len(st.session_state.messages) == 0:
    st.markdown("<br>", unsafe_allow_html=True) # Spacer
    
    col1, col2 = st.columns(2)
    
    # We use callback functions to handle button clicks cleanly
    def submit_suggestion(text):
        st.session_state.messages.append({"role": "user", "content": text})
        # Note: In Streamlit, to trigger the API call immediately after a button click 
        # usually requires a rerun or setting a flag. For simplicity in this layout,
        # we append to history. The user might need to hit enter or we use a flag logic.
        # But visually, this sets the stage.
    
    with col1:
        if st.button("Find 2BHK in Bangalore < 1Cr"):
            submit_suggestion("Find a 2BHK in Bangalore under 1 Cr")
            st.rerun()
        if st.button("Show villas with private pool"):
            submit_suggestion("Show me villas with a pool")
            st.rerun()
            
    with col2:
        if st.button("Investment hotspots 2024"):
            submit_suggestion("What are the best areas for investment?")
            st.rerun()
        if st.button("Rental yields in Mumbai"):
            submit_suggestion("Rental trends in Mumbai South")
            st.rerun()

# --- CHAT INPUT & LOGIC ---
# We check if the last message was from the user (handling the button click case)
# OR if the user just typed into the input box.

user_input = st.chat_input("Initialize query protocol...")

# Logic: If user entered text OR if the last message in history is USER (from button click) 
# AND the very last message is NOT assistant (meaning we haven't answered yet).
should_run_api = False
prompt_text = ""

if user_input:
    prompt_text = user_input
    with st.chat_message("user"):
        st.markdown(prompt_text)
    st.session_state.messages.append({"role": "user", "content": prompt_text})
    should_run_api = True

elif len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] == "user":
    # This catches the button click case after the rerun
    prompt_text = st.session_state.messages[-1]["content"]
    should_run_api = True

# --- API EXECUTION ---
if should_run_api:
    with st.spinner("Accessing property database..."):
        try:
            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "message": prompt_text,
                "sessionId": st.session_state.session_id
            }

            response = requests.get(API_URL, headers=headers, json=payload, timeout=120)
            response.raise_for_status()

            backend_response = response.json()
            assistant_reply = backend_response.get("reply", "Database connection error.")

            with st.chat_message("assistant"):
                st.markdown(assistant_reply)

            st.session_state.messages.append({"role": "assistant", "content": assistant_reply})

        except requests.exceptions.RequestException as e:
            st.error(f"Network Error: {e}")
            # If error, remove the user's last message so they can try again
            if len(st.session_state.messages) > 0:
                st.session_state.messages.pop()
