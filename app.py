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

# --- CUSTOM CSS (The Luxury Dashboard Theme) ---
st.markdown("""
<style>
    /* 1. IMPORT FONTS */
    /* Oswald = The "Long/Tall" Architectural Font */
    /* Inter = Clean, readable body font */
    @import url('https://fonts.googleapis.com/css2?family=Oswald:wght@300;500&family=Inter:wght@300;400;600&display=swap');

    /* 2. BACKGROUND & STRUCTURE */
    .stApp {
        /* subtle gradient to kill the "flat black" look */
        background: radial-gradient(circle at 50% 10%, #1E2329 0%, #0D1117 100%);
    }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #E0E0E0;
    }

    /* 3. TYPOGRAPHY overrides */
    h1, h2, h3 {
        font-family: 'Oswald', sans-serif !important;
        font-weight: 500 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .hero-container {
        text-align: center;
        padding: 40px 0;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        margin-bottom: 30px;
    }

    .hero-title {
        font-size: 3.5rem;
        font-weight: 300;
        background: -webkit-linear-gradient(90deg, #A8C0FF, #3f2b96); /* Elegant Blue/Purple Gradient */
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    
    .hero-subtitle {
        color: #8b9bb4;
        font-size: 1.1rem;
        margin-top: 10px;
        font-family: 'Inter', sans-serif;
    }

    /* 4. BUTTONS / CARDS STYLING */
    /* This makes the suggestion buttons look like premium cards */
    div.stButton > button {
        width: 100%;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        color: #c9d1d9;
        padding: 20px 15px;
        font-family: 'Inter', sans-serif;
        font-size: 0.95rem;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        text-align: left;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    div.stButton > button:hover {
        background: rgba(255, 255, 255, 0.08);
        border-color: #58a6ff; /* Soft Blue highlight */
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        color: #fff;
    }

    /* 5. CHAT MESSAGES */
    /* Remove default bubble backgrounds for a cleaner look */
    .stChatMessage {
        background-color: transparent !important;
    }
    
    /* Avatar containers */
    .stChatMessage .st-emotion-cache-1p1m4ay {
        border-radius: 50%;
    }

    /* 6. INPUT BAR */
    .stChatInput {
        padding-bottom: 30px;
    }
    
    .stChatInput textarea {
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
        color: white !important;
        border-radius: 10px !important;
    }
    
    .stChatInput textarea:focus {
        border-color: #58a6ff !important;
        box-shadow: 0 0 0 2px rgba(88, 166, 255, 0.2) !important;
    }

    /* Hide standard UI elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# --- API CONFIG ---
try:
    API_URL = st.secrets["api"]["url"]
    API_KEY = st.secrets["api"]["key"]
except KeyError:
    API_URL = "http://localhost:3000/chat"
    API_KEY = "test"

# --- SIDEBAR ---
with st.sidebar:
    st.title("RELΛI")
    st.markdown("Your AI Property Expert.")
    
    st.markdown("---")
    if st.button("New Search ⟳", use_container_width=True):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()
    
    st.markdown("### Contact")
    st.link_button("Chat on WhatsApp 💬", "https://api.whatsapp.com/send/?phone=917331112955", use_container_width=True)

# --- MAIN HERO HEADER ---
# This only shows if the chat is empty, to keep the top clean during conversation
if len(st.session_state.messages) == 0:
    st.markdown("""
        <div class="hero-container">
            <h1 class="hero-title">RELAI INTELLIGENCE</h1>
            <p class="hero-subtitle">Data-driven property insights. Ask me anything.</p>
        </div>
    """, unsafe_allow_html=True)

# --- CHAT HISTORY ---
# We iterate through history. We can assign specific icons for role styling.
for message in st.session_state.messages:
    # Set icons based on role
    icon = "👤" if message["role"] == "user" else "🏢"
    with st.chat_message(message["role"], avatar=icon):
        st.markdown(message["content"])

# --- SUGGESTIONS (Empty State) ---
if len(st.session_state.messages) == 0:
    st.write("") # Spacer
    col1, col2 = st.columns(2)
    
    # Helper to process suggestion clicks
    def handle_click(text):
        st.session_state.messages.append({"role": "user", "content": text})
        # Rerun not strictly necessary if we rely on next script execution, 
        # but helpful for instant feedback.
    
    with col1:
        if st.button("🔍 Find a 3BHK in Indiranagar < 2Cr"):
            st.session_state.messages.append({"role": "user", "content": "Find a 3BHK in Indiranagar under 2 Crores"})
            st.rerun()
        if st.button("🏊 Show me villas with private pools"):
            st.session_state.messages.append({"role": "user", "content": "Show me villas with private pools"})
            st.rerun()

    with col2:
        if st.button("📈 Top 5 Investment Areas 2025"):
            st.session_state.messages.append({"role": "user", "content": "What are the top 5 investment areas for 2025?"})
            st.rerun()
        if st.button("💰 Rental Yield Analysis: Mumbai"):
            st.session_state.messages.append({"role": "user", "content": "Give me a rental yield analysis for Mumbai"})
            st.rerun()

# --- INPUT & LOGIC ---
# Standard input, but styled by CSS above
prompt = st.chat_input("Ask about properties, trends, or specific locations...")

# Logic: Check if we have a prompt (typed) OR a pending suggestion (from button click history)
# We need to detect if the last message is USER and we haven't answered it yet.
last_message_is_user = len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] == "user"
last_message_is_assistant = len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] == "assistant"

process_queue = False

if prompt:
    # 1. User typed something
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    process_queue = True

elif last_message_is_user and not last_message_is_assistant:
    # 2. User clicked a button (which added to history) but we haven't replied yet
    process_queue = True

if process_queue:
    # Get the text to send
    user_text = st.session_state.messages[-1]["content"]
    
    with st.chat_message("assistant", avatar="🏢"):
        with st.spinner("Analyzing market data..."):
            try:
                headers = {
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "message": user_text,
                    "sessionId": st.session_state.session_id
                }

                response = requests.get(API_URL, headers=headers, json=payload, timeout=120)
                response.raise_for_status()

                data = response.json()
                reply = data.get("reply", "I received the data but the response format was unexpected.")
                
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})

            except requests.exceptions.RequestException as e:
                error_msg = f"Unable to connect to Real Estate Database. Error: {e}"
                st.error(error_msg)
                # Remove the user message if it failed, so they can try again? 
                # Or just leave it. Leaving it is usually better UX so they can copy-paste.
