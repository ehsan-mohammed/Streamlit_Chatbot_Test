import time
import uuid
import requests
import streamlit as st
from collections import deque
from streamlit.web.server.websocket_headers import _get_websocket_headers

# --- CONFIGURATION ---
PAGE_TITLE = "ChatBot Prototype"
PAGE_ICON = "🤖"
API_TIMEOUT = 120 

# RATE LIMIT SETTINGS
MAX_REQ_PER_MINUTE = 5   # Max messages per IP per minute
BLOCK_TIME_SECONDS = 60  # How long to block them if they exceed limits

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

# --- GLOBAL RATE LIMITER (The "Bouncer") ---
# @st.cache_resource ensures this object is created ONCE and shared across all users.
# It does not get wiped when a user refreshes or clicks reset.

@st.cache_resource
class RateLimiter:
    def __init__(self):
        self.requests = {} # Stores {ip: deque([timestamp1, timestamp2...])}

    def is_rate_limited(self, ip):
        now = time.time()
        
        # 1. Initialize if new IP
        if ip not in self.requests:
            self.requests[ip] = deque()

        # 2. Clean up old requests (older than 1 minute)
        # We peek at the left (oldest) and pop if it's expired
        while self.requests[ip] and self.requests[ip][0] < now - 60:
            self.requests[ip].popleft()

        # 3. Check specific block conditions
        if len(self.requests[ip]) >= MAX_REQ_PER_MINUTE:
            return True
        
        return False

    def add_request(self, ip):
        self.requests[ip].append(time.time())

# Instantiate the global limiter
limiter = RateLimiter()

def get_remote_ip():
    """Attempts to get the client IP address from request headers."""
    try:
        headers = _get_websocket_headers()
        # X-Forwarded-For is the standard header for identifying IPs behind a load balancer
        return headers.get("X-Forwarded-For", "unknown_ip")
    except:
        return "unknown_ip"

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

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
        st.session_state.processing = False 
        st.rerun()

st.divider()

# --- CHAT HISTORY ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        st.caption(message.get("time", ""))

# --- CHAT INPUT & LOGIC ---

prompt = st.chat_input(
    "How can I help you today?", 
    disabled=st.session_state.processing, 
    on_submit=lock_input
)

if prompt:
    # --- 1. GLOBAL SECURITY CHECK ---
    user_ip = get_remote_ip()
    
    # Check if this IP is abusing the system
    if limiter.is_rate_limited(user_ip):
        st.error(f"⛔ Rate limit exceeded. You are sending too many requests. Please wait a minute.")
        st.session_state.processing = False # Unlock so they can see the error, but don't run logic
        st.stop() # HALT execution immediately

    # If they pass, log this request
    limiter.add_request(user_ip)

    # --- 2. RENDER USER MESSAGE ---
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "time": time.strftime("%I:%M %p")  # e.g. "03:45 PM"
    })    

    # --- 3. API CALL ---
    with st.spinner("Thinking..."):
        try:
            headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
            payload = {"message": prompt, "sessionId": st.session_state.session_id}
            
            response = requests.get(API_URL, headers=headers, json=payload, timeout=API_TIMEOUT)
            response.raise_for_status()
            
            assistant_reply = response.json().get("reply", "I'm sorry, I couldn't generate a response.")

            with st.chat_message("assistant"):
                st.markdown(assistant_reply)
            st.session_state.messages.append({
                "role": "assistant",
                "content": assistant_reply,
                "time": time.strftime("%I:%M %p")
            })

        except requests.exceptions.RequestException as e:
            st.error("Could not connect to the AI agent. Please try again later.")
        
        finally:
            st.session_state.processing = False
            st.rerun()
