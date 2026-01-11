# app.py

import streamlit as st
import requests
import uuid
import base64
from pathlib import Path

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="ChatBot Prototype",
    page_icon="🤖",
    layout="centered"
)

# --- FUNCTION TO LOAD BACKGROUND IMAGE ---
def get_base64_of_bin_file(png_file):
    """Convert local image to base64"""
    try:
        with open(png_file, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return None

# Load background image (name it 'background.jpg' in the same folder as app.py)
img_file = Path("background.jpg")
if img_file.exists():
    img_base64 = get_base64_of_bin_file(img_file)
    bg_image = f"data:image/jpeg;base64,{img_base64}"
else:
    bg_image = None

# --- CUSTOM CSS ---
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600&display=swap');
    
    /* Global Styles */
    * {{
        font-family: 'Space Grotesk', sans-serif !important;
    }}
    
    /* Main background with image */
    .stApp {{
        background: {'linear-gradient(rgba(15, 23, 42, 0.85), rgba(15, 23, 42, 0.85)), url(' + bg_image + ') center/cover no-repeat fixed' if bg_image else 'linear-gradient(180deg, #0f172a 0%, #1e293b 100%)'};
        position: relative;
    }}
    
    /* Gradient overlay at bottom for smooth transition */
    .stApp::after {{
        content: '';
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        height: 200px;
        background: linear-gradient(to bottom, transparent 0%, rgba(15, 23, 42, 0.7) 50%, rgba(15, 23, 42, 0.95) 100%);
        pointer-events: none;
        z-index: 1;
    }}
    
    /* Main container styling */
    .main .block-container {{
        padding: 3rem 2rem;
        max-width: 800px;
        position: relative;
        z-index: 2;
    }}
    
    /* Title styling */
    h1 {{
        color: #ffffff !important;
        font-weight: 500 !important;
        font-size: 2.25rem !important;
        letter-spacing: -0.01em;
        margin-bottom: 1.5rem !important;
        text-align: center;
    }}
    
    /* Subtitle text */
    .main p {{
        color: rgba(255, 255, 255, 0.75) !important;
        font-size: 1.05rem !important;
        font-weight: 300 !important;
        text-align: center !important;
        margin-bottom: 2rem !important;
    }}
    
    /* Button styling - square, no border radius */
    .stButton button {{
        background: rgba(255, 255, 255, 0.08) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 0 !important;
        padding: 0.75rem 2rem !important;
        font-weight: 400 !important;
        font-size: 0.95rem !important;
        transition: all 0.2s ease !important;
        backdrop-filter: blur(10px) !important;
        letter-spacing: 0.02em;
    }}
    
    .stButton button:hover {{
        background: rgba(255, 255, 255, 0.12) !important;
        border-color: rgba(255, 255, 255, 0.25) !important;
    }}
    
    /* Hide default streamlit chat avatars */
    .stChatMessage img {{
        display: none !important;
    }}
    
    /* Chat message containers - remove border radius */
    .stChatMessage {{
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 0 !important;
        padding: 1rem 1.25rem !important;
        margin: 0.5rem 0 !important;
    }}
    
    /* User message styling */
    .stChatMessage[data-testid="user-message"] {{
        background: rgba(59, 130, 246, 0.1) !important;
        border-color: rgba(59, 130, 246, 0.2) !important;
    }}
    
    /* Assistant message styling */
    .stChatMessage[data-testid="assistant-message"] {{
        background: rgba(255, 255, 255, 0.05) !important;
    }}
    
    /* Chat message text */
    .stChatMessage p {{
        color: rgba(255, 255, 255, 0.95) !important;
        font-size: 0.95rem !important;
        line-height: 1.6 !important;
        text-align: left !important;
        font-weight: 300 !important;
        margin: 0 !important;
    }}
    
    /* Chat input container - KEEP CURVED */
    .stChatInputContainer {{
        background: rgba(20, 30, 48, 0.9) !important;
        backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 24px !important;
        padding: 0.5rem !important;
        position: relative;
        z-index: 3;
    }}
    
    /* Chat input field */
    .stChatInput textarea {{
        background: transparent !important;
        color: white !important;
        border: none !important;
        font-size: 0.95rem !important;
        font-weight: 300 !important;
    }}
    
    .stChatInput textarea::placeholder {{
        color: rgba(255, 255, 255, 0.4) !important;
    }}
    
    /* Spinner */
    .stSpinner > div {{
        border-top-color: #60a5fa !important;
    }}
    
    /* Error messages */
    .stAlert {{
        background: rgba(239, 68, 68, 0.1) !important;
        border: 1px solid rgba(239, 68, 68, 0.2) !important;
        border-radius: 0 !important;
        color: #fca5a5 !important;
        font-weight: 300 !important;
    }}
    
    /* Column adjustments */
    [data-testid="column"] {{
        padding: 0 0.5rem !important;
    }}
    
    /* Hide Streamlit branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    /* Responsive adjustments */
    @media (max-width: 768px) {{
        .main .block-container {{
            padding: 2rem 1rem;
        }}
        
        h1 {{
            font-size: 1.75rem !important;
        }}
        
        .main > div > div > div > p {{
            font-size: 0.95rem;
        }}
        
        .stButton button {{
            padding: 0.65rem 1.5rem !important;
            font-size: 0.9rem !important;
        }}
        
        .stApp::after {{
            height: 150px;
        }}
    }}
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

# Center-aligned buttons
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    st.write("")

with col2:
    st.link_button("Launch 🚀", "https://api.whatsapp.com/send/?phone=917331112955&text=Hi%21+I+need+help+with+property+recommendations.&type=phone_number&app_absent=0", use_container_width=True)
    if st.button("Reset Session 🔄", use_container_width=True):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

with col3:
    st.write("")

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
