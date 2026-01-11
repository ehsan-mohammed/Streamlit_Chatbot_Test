# app.py

import streamlit as st
import requests
import uuid
import base64

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="ChatBot Prototype",
    page_icon="🤖",
    layout="centered"
)

# --- CUSTOM CSS ---
def get_base64_image(image_path):
    """Convert image to base64 for CSS background"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None

# Custom CSS with mountain background and modern styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    /* Main background with image */
    .stApp {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.92) 100%),
                    url('data:image/jpeg;base64,/9j/4AAQSkZJRg...') center/cover no-repeat fixed;
        background-blend-mode: overlay;
    }
    
    /* Fallback gradient background */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
        z-index: -1;
    }
    
    /* Main container styling */
    .main .block-container {
        padding: 2rem 1rem;
        max-width: 900px;
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        border-radius: 32px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
        margin-top: 2rem;
    }
    
    /* Title styling */
    h1 {
        background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700 !important;
        font-size: 2.5rem !important;
        letter-spacing: -0.02em;
        margin-bottom: 1rem !important;
        text-align: center;
    }
    
    /* Subtitle text */
    .main p {
        color: rgba(255, 255, 255, 0.8) !important;
        font-size: 1.1rem;
        font-weight: 400;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Button styling */
    .stButton button {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 16px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 20px rgba(59, 130, 246, 0.4) !important;
        letter-spacing: 0.02em;
    }
    
    .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 30px rgba(59, 130, 246, 0.6) !important;
    }
    
    /* Link button specific styling */
    .stButton a {
        text-decoration: none !important;
    }
    
    /* Chat message containers */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 20px !important;
        padding: 1rem 1.5rem !important;
        margin: 0.75rem 0 !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2) !important;
    }
    
    /* User message styling */
    .stChatMessage[data-testid="user-message"] {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(139, 92, 246, 0.15) 100%) !important;
        border-color: rgba(59, 130, 246, 0.3) !important;
    }
    
    /* Assistant message styling */
    .stChatMessage[data-testid="assistant-message"] {
        background: rgba(255, 255, 255, 0.08) !important;
    }
    
    /* Chat message text */
    .stChatMessage p {
        color: rgba(255, 255, 255, 0.95) !important;
        font-size: 1rem !important;
        line-height: 1.6 !important;
        text-align: left !important;
    }
    
    /* Chat input container */
    .stChatInputContainer {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 24px !important;
        padding: 0.5rem !important;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3) !important;
    }
    
    /* Chat input field */
    .stChatInput textarea {
        background: transparent !important;
        color: white !important;
        border: none !important;
        font-size: 1rem !important;
        font-weight: 400 !important;
    }
    
    .stChatInput textarea::placeholder {
        color: rgba(255, 255, 255, 0.5) !important;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #60a5fa !important;
    }
    
    /* Error messages */
    .stAlert {
        background: rgba(239, 68, 68, 0.1) !important;
        border: 1px solid rgba(239, 68, 68, 0.3) !important;
        border-radius: 16px !important;
        color: #fca5a5 !important;
    }
    
    /* Column containers */
    .row-widget.stHorizontal {
        gap: 1rem;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1.5rem 1rem;
            border-radius: 24px;
            margin-top: 1rem;
        }
        
        h1 {
            font-size: 2rem !important;
        }
        
        .main p {
            font-size: 1rem;
        }
        
        .stButton button {
            padding: 0.6rem 1.5rem !important;
            font-size: 0.9rem !important;
        }
    }
    
    /* Smooth scrolling */
    html {
        scroll-behavior: smooth;
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
    st.error("API URL/Key not found. Please add them to your Streamlit secrets.")
    st.stop()

# --- UI & LOGIC ---
st.title("WhatsApp Chat Bot 2.0 Prototype 🤖")
st.write("I am a Relai Expert real-estate AI Agent ready to help you find your ideal property.")

# Create two columns for the buttons
col1, col2 = st.columns([1, 1])

with col1:
    st.link_button("Launch 🚀", "https://api.whatsapp.com/send/?phone=917331112955&text=Hi%21+I+need+help+with+property+recommendations.&type=phone_number&app_absent=0")

with col2:
    if st.button("Reset Session 🔄"):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

# Add spacing
st.markdown("<div style='margin: 2rem 0'></div>", unsafe_allow_html=True)
        
# Display existing chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("How can I help you today?"):
    # 1. Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 3. Call the backend API
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

            # 4. Process the response
            backend_response = response.json()
            assistant_reply = backend_response.get("reply", "Sorry, I encountered an error.")

            # 5. Display assistant response in chat message container
            with st.chat_message("assistant"):
                st.markdown(assistant_reply)

            # 6. Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": assistant_reply})

        except requests.exceptions.RequestException as e:
            st.error(f"Could not connect to the AI agent. Please try again later. Error: {e}")
            st.session_state.messages.pop()
