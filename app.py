import streamlit as st
import requests
import uuid
import base64
import os

# --- HELPER: CONVERT SVG TO BASE64 FOR CSS ---
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return None

# --- LOAD ICONS ---
# specific filenames for your icons
img_robot  = get_base64_of_bin_file("icon_robot.svg")
img_rocket = get_base64_of_bin_file("icon_rocket.svg")
img_reset  = get_base64_of_bin_file("icon_reset.svg")

# --- PAGE CONFIGURATION (Place 1: Page Icon) ---
# st.set_page_config accepts a file path directly for the favicon
st.set_page_config(
    page_title="ChatBot Prototype",
    page_icon="icon_page.svg", 
    layout="centered"
)

# --- CUSTOM CSS ---
# We inject the Base64 images directly into the button CSS
st.markdown(f"""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Zalando+Sans+Expanded:ital,wght@0,200..900;1,200..900&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Recursive:wght@300..1000&display=swap" rel="stylesheet">

<style>
    /* FONTS */
    h1, .subtitle, .stButton button, .stLinkButton a {{
        font-family: "Zalando Sans Expanded", sans-serif !important;
    }}
    
    .stChatMessage, .stChatMessage * {{
        font-family: "Recursive", sans-serif !important;
    }}

    /* --- PLACE 3: CUSTOM LAUNCH BUTTON ICON (ROCKET) --- */
    /* Target the Link Button (Launch) */
    div[data-testid="stLinkButton"] a {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 10px; /* Space between text and icon */
        font-weight: 600 !important;
    }}
    
    /* Inject the Rocket Icon via CSS pseudo-element */
    div[data-testid="stLinkButton"] a::after {{
        content: "";
        display: inline-block;
        width: 20px;
        height: 20px;
        background-image: url("data:image/svg+xml;base64,{img_rocket}");
        background-size: contain;
        background-repeat: no-repeat;
        background-position: center;
    }}

    /* --- PLACE 4: CUSTOM RESET BUTTON ICON (ARROWS) --- */
    /* Target the Standard Button (Reset) */
    div[data-testid="stButton"] button {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        font-weight: 600 !important;
    }}
    
    /* Inject the Reset Icon via CSS pseudo-element */
    div[data-testid="stButton"] button::after {{
        content: "";
        display: inline-block;
        width: 20px;
        height: 20px;
        background-image: url("data:image/svg+xml;base64,{img_reset}");
        background-size: contain;
        background-repeat: no-repeat;
        background-position: center;
    }}
    
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# --- API ---
try:
    API_URL = st.secrets["api"]["url"]
    API_KEY = st.secrets["api"]["key"]
except KeyError:
    API_URL = "http://localhost:8000"
    API_KEY = "test"

# --- UI HEADER (Place 2: Title Icon) ---
# We use an HTML <img> tag to render the SVG directly in the title
icon_html = f'<img src="data:image/svg+xml;base64,{img_robot}" style="width: 45px; height: 45px; margin-left: 10px; vertical-align: bottom;">' if img_robot else "🤖"

st.markdown(
    f"""
    <h1 style='text-align: center;'>
        WhatsApp Chat Bot 2.0 Prototype {icon_html}
    </h1>
    <p class="subtitle" style='text-align: center; font-family: "Zalando Sans Expanded"; margin-bottom: 2rem;'>
        I am a Relai Expert real-estate AI Agent ready to help you find your ideal property.
    </p>
    """, 
    unsafe_allow_html=True
)

# --- BUTTONS ---
col1, col_btn1, col_btn2, col2 = st.columns([1, 2, 2, 1])

with col_btn1:
    # Note: We removed the emoji from the text string because CSS adds it now
    st.link_button(
        "Launch", 
        "https://api.whatsapp.com/send?phone=...",
        use_container_width=True
    )

with col_btn2:
    # Note: We removed the emoji here too
    if st.button("Reset", use_container_width=True):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

# --- CHAT ---
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
            # Fake logic for demo
            assistant_reply = "This is a response."
            st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
            st.rerun() 
        except Exception:
            pass
