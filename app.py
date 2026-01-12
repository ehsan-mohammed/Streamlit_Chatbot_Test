import streamlit as st
import requests
import uuid

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="ChatBot Prototype",
    page_icon="🤖",
    layout="centered"
)

# --- CUSTOM CSS FOR CENTERED LAYOUT AND FONT ---
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
    
    /* Apply Zalando Sans Expanded to buttons */
    .stButton > button,
    .stButton > a {
        font-family: "Zalando Sans Expanded", sans-serif !important;
    }
    
    /* Center buttons wrapper */
    .button-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 1rem;
        width: 100%;
        margin: 2rem 0;
    }
    
    /* Center all buttons */
    .button-wrapper .stButton,
    .stButton {
        display: flex;
        justify-content: center;
        width: 100%;
    }
    
    .stButton > button,
    .stButton > a {
        display: block;
        margin: 0 auto !important;
    }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
# This is crucial for maintaining the chat history and a unique session ID per user.
# The session ID is sent to your backend to retrieve the correct Postgres chat memory.

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize a unique session ID
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# --- BACKEND API DETAILS ---
# Load secrets from the .streamlit/secrets.toml file
try:
    API_URL = st.secrets["api"]["url"]
    API_KEY = st.secrets["api"]["key"]
except KeyError:
    st.error("API URL/Key not found. Please add them to your Streamlit secrets.")
    st.stop()

# --- UI & LOGIC ---
st.title("WhatsApp Chat Bot 2.0 Prototype 🤖")
st.markdown('<p class="subtitle">I am a Relai Expert real-estate AI Agent ready to help you find your ideal property.</p>', unsafe_allow_html=True)

# Center the buttons - use markdown for better centering control
st.markdown('<div class="button-wrapper">', unsafe_allow_html=True)
st.link_button("Launch 🚀", "https://api.whatsapp.com/send/?phone=917331112955&text=Hi%21+I+need+help+with+property+recommendations.&type=phone_number&app_absent=0")
if st.button("Reset Session 🔄"):
    st.session_state.messages = []
    st.session_state.session_id = str(uuid.uuid4())
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)
        
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
            response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)

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
            # Optionally remove the user's last message to allow them to retry
            st.session_state.messages.pop()
