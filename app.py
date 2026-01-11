import streamlit as st
import requests
import uuid

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Relai Estate",
    page_icon="🏛️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- LUXURY STYLING ---
st.markdown("""
<style>
    /* 1. LOAD PREMIUM FONTS */
    /* Cinzel: Luxury Serif for Headers */
    /* Lato: Clean, high-end sans-serif for body */
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Lato:wght@300;400;700&display=swap');

    /* 2. BACKGROUND */
    .stApp {
        /* Deep Midnight Blue Gradient */
        background: linear-gradient(135deg, #0a1128 0%, #000000 100%);
    }

    html, body, [class*="css"] {
        font-family: 'Lato', sans-serif;
        color: #E0E0E0;
    }

    /* 3. TYPOGRAPHY */
    h1, h2, h3 {
        font-family: 'Cinzel', serif !important;
        font-weight: 700 !important;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #D4AF37; /* Metallic Gold */
    }

    .hero-title {
        font-size: 3.8rem;
        background: linear-gradient(to right, #D4AF37, #F2D06B, #D4AF37);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 10px;
        text-shadow: 0px 4px 10px rgba(0,0,0,0.5);
    }
    
    .hero-subtitle {
        text-align: center;
        color: #8fa3b0;
        font-size: 1.1rem;
        font-weight: 300;
        margin-bottom: 50px;
        font-family: 'Lato', sans-serif;
    }

    /* 4. CHAT BUBBLES */
    .stChatMessage {
        background-color: transparent !important;
        border: none !important;
    }
    
    /* User: Subtle Blue tint */
    .stChatMessage[data-testid="stChatMessage"]:nth-child(odd) {
        background: rgba(255, 255, 255, 0.05) !important;
        border-radius: 20px;
        border-bottom-right-radius: 2px;
        padding: 15px;
        margin-bottom: 10px;
        border: 1px solid rgba(255,255,255,0.05) !important;
    }
    
    /* Assistant: Transparent with Gold accent */
    .stChatMessage[data-testid="stChatMessage"]:nth-child(even) {
        background: transparent !important;
        border-left: 2px solid #D4AF37 !important; /* Gold Line */
        padding-left: 20px;
    }

    /* 5. FIXING THE INPUT BAR */
    /* This targets the container to remove the blocky look */
    .stChatInput {
        background: transparent !important;
    }
    
    .stChatInput textarea {
        background-color: #0f1623 !important; /* Darker than background */
        color: #D4AF37 !important; /* Gold Text */
        border: 1px solid #334155 !important;
        border-radius: 50px !important; /* Fully rounded pill shape */
        padding: 15px 25px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
    }
    
    .stChatInput textarea:focus {
        border-color: #D4AF37 !important; /* Gold Border on focus */
        box-shadow: 0 0 15px rgba(212, 175, 55, 0.2) !important;
    }
    
    /* Hide the 'Attach' button inside input if possible, or style it */
    button[kind="secondaryFormSubmit"] {
        border: none;
        background: transparent;
        color: #D4AF37;
    }

    /* 6. BUTTON CARDS */
    div.stButton > button {
        background: linear-gradient(145deg, #1e293b, #0f172a);
        color: #cbd5e1;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 20px;
        font-family: 'Cinzel', serif; /* Using luxury font for buttons too */
        text-align: center;
        transition: all 0.3s ease;
        text-transform: uppercase;
        font-size: 0.85rem;
        letter-spacing: 1px;
    }

    div.stButton > button:hover {
        border-color: #D4AF37;
        color: #D4AF37;
        background: #0f172a;
        transform: translateY(-3px);
        box-shadow: 0 5px 15px rgba(212, 175, 55, 0.15);
    }

    /* Hide standard Streamlit chrome */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)

# --- SESSION & API ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

try:
    API_URL = st.secrets["api"]["url"]
    API_KEY = st.secrets["api"]["key"]
except KeyError:
    API_URL = "http://localhost:3000/chat"
    API_KEY = "test"

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### RELAI PRIME")
    if st.button("NEW CONSULTATION", use_container_width=True):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

# --- HERO HEADER ---
# Only visible when chat is empty
if len(st.session_state.messages) == 0:
    st.markdown('<div class="hero-title">RELAI</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">The Gold Standard in Property Intelligence</div>', unsafe_allow_html=True)

# --- CHAT HISTORY ---
for message in st.session_state.messages:
    # Custom avatars: A simple user icon and a building for the bot
    avatar = "👤" if message["role"] == "user" else "🏛️"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# --- EMPTY STATE CARDS ---
if len(st.session_state.messages) == 0:
    st.write("") # Spacer
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Luxury Villas > 5 Cr"):
            st.session_state.messages.append({"role": "user", "content": "Show me luxury villas above 5 Crores"})
            st.rerun()
        if st.button("Market Analysis 2025"):
             st.session_state.messages.append({"role": "user", "content": "What is the market outlook for 2025?"})
             st.rerun()

    with col2:
        if st.button("High Yield Rentals"):
             st.session_state.messages.append({"role": "user", "content": "Where can I find high rental yield properties?"})
             st.rerun()
        if st.button("Schedule Visit"):
             st.session_state.messages.append({"role": "user", "content": "I want to schedule a site visit."})
             st.rerun()

# --- INPUT LOGIC ---
prompt = st.chat_input("Inquire about a property...")

# Handling the "Button Click" vs "Type" logic
last_msg_user = len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] == "user"
last_msg_asst = len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] == "assistant"

if prompt:
    # User typed manually
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    
    # Process immediately
    with st.chat_message("assistant", avatar="🏛️"):
        with st.spinner("Consulting database..."):
            try:
                headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
                payload = {"message": prompt, "sessionId": st.session_state.session_id}
                response = requests.get(API_URL, headers=headers, json=payload, timeout=120)
                response.raise_for_status()
                reply = response.json().get("reply", "Error parsing response.")
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            except Exception as e:
                st.error(f"Service unavailable: {e}")

elif last_msg_user and not last_msg_asst:
    # User clicked a button, history is updated, but no reply yet
    user_text = st.session_state.messages[-1]["content"]
    with st.chat_message("assistant", avatar="🏛️"):
        with st.spinner("Consulting database..."):
            try:
                headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
                payload = {"message": user_text, "sessionId": st.session_state.session_id}
                response = requests.get(API_URL, headers=headers, json=payload, timeout=120)
                response.raise_for_status()
                reply = response.json().get("reply", "Error parsing response.")
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            except Exception as e:
                st.error(f"Service unavailable: {e}")
