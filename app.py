import streamlit as st
import requests
import uuid

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Relai Estate Agent",
    page_icon="🏡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CUSTOM CSS & STYLING ---
# This hides the default Streamlit menu/footer and styles buttons to look premium
st.markdown("""
<style>
    /* Import a nice font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }

    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Style the main title */
    .main-title {
        text-align: center;
        font-weight: 600;
        font-size: 2.5rem;
        background: -webkit-linear-gradient(45deg, #25D366, #128C7E); /* WhatsApp Green Gradient */
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    
    .sub-title {
        text-align: center;
        color: #888;
        font-size: 1.1rem;
        margin-bottom: 30px;
    }

    /* Suggestion Cards */
    .suggestion-btn {
        border: 1px solid #333;
        border-radius: 10px;
        padding: 10px;
        text-align: center;
        background-color: #0e1117;
        color: white;
        transition: 0.3s;
        cursor: pointer;
    }
    .suggestion-btn:hover {
        border-color: #25D366;
        background-color: #1a1f26;
    }

    /* Chat Input Styling */
    .stChatInput {
        padding-bottom: 20px;
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
    # Ensure you have these in .streamlit/secrets.toml
    API_URL = st.secrets["api"]["url"]
    API_KEY = st.secrets["api"]["key"]
except KeyError:
    # Fallback for testing if secrets aren't set up yet
    API_URL = "http://localhost:3000/chat" 
    API_KEY = "test"
    # st.error("API URL/Key not found. Please check secrets.")
    # st.stop()

# --- SIDEBAR (ADMIN & CONTROLS) ---
with st.sidebar:
    st.title("⚙️ Controls")
    st.write("Manage your session here.")
    
    if st.button("New Chat / Reset 🔄", use_container_width=True):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

    st.markdown("---")
    st.markdown("### 📱 Mobile Experience")
    st.link_button("Open in WhatsApp 🚀", "https://api.whatsapp.com/send/?phone=917331112955&text=Hi%21+I+need+help+with+property+recommendations.", use_container_width=True)

# --- UI HEADER ---
st.markdown('<div class="main-title">Relai AI Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Your expert real-estate companion. <br> Ask me about properties, prices, and locations.</div>', unsafe_allow_html=True)

# --- DISPLAY CHAT HISTORY ---
# We display the chat history first so it stays on screen
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- EMPTY STATE SUGGESTIONS ---
# If chat is empty, show clickable suggestion chips to help the user start
if len(st.session_state.messages) == 0:
    st.markdown("Or try one of these examples:")
    cols = st.columns(2)
    
    # Helper function to handle button clicks
    def set_prompt(text):
        st.session_state.messages.append({"role": "user", "content": text})
        st.rerun() # Rerun to trigger the "React to user input" block logic requires a small refactor or just manual submission.
        # Note: Streamlit buttons usually don't autofill chat input easily without callbacks. 
        # For simplicity in this structure, we will just display text examples below.

    with cols[0]:
        st.info("Find a 2BHK in Bangalore under 1 Cr")
    with cols[1]:
        st.info("What are the best areas for investment?")
    with cols[0]:
        st.info("Show me villas with a pool")
    with cols[1]:
        st.info("Rental trends in Mumbai South")

# --- CHAT LOGIC ---
if prompt := st.chat_input("Ask about your dream home..."):
    # 1. Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Add to history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 3. Call API
    with st.spinner("Analyzing property market..."):
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
            assistant_reply = backend_response.get("reply", "I found some info, but couldn't parse the reply.")

            # 4. Display assistant response
            with st.chat_message("assistant"):
                st.markdown(assistant_reply)

            # 5. Add assistant response to history
            st.session_state.messages.append({"role": "assistant", "content": assistant_reply})

        except requests.exceptions.RequestException as e:
            st.error(f"Connection error: {e}")
            st.session_state.messages.pop() # Remove user prompt so they can try again
