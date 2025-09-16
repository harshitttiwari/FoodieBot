# app.py
import streamlit as st
from database import initialize_services
from bot_logic import initialize_llm
from ui_components import render_chat_interface, render_analytics_sidebar, render_admin_panel

st.set_page_config(
    page_title="FoodieBot Live Demo",
    page_icon="🤖",
    layout="wide",
)

# --- Styling ---
st.markdown(
    """
    <style>
    .main .block-container {padding-top: 1rem;}
    .stChatMessage {max-height: 350px; overflow-y: auto;}
    </style>
    """,
    unsafe_allow_html=True
)

# --- Init Phase ---
if "app_ready" not in st.session_state:
    with st.spinner("🚀 Initializing services... Please wait."):
        # Load .env for local development
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            # This is normal on Hugging Face, no message needed
            pass

        # Initialize all services
        df, collection, embedder = initialize_services()
        llm = initialize_llm()

        # Check if services loaded correctly
        if df is None:
            st.error("Stopping app due to data loading failure.")
            st.stop()
        if collection is None or embedder is None:
            st.error("Stopping app due to vector DB or embedding failure.")
            st.stop()
        if llm is None:
            st.error("Stopping app due to LLM initialization failure. Check your GROQ_API_KEY secret.")
            st.stop()
        
        # Save services and state to the session
        st.session_state.df = df
        st.session_state.collection = collection
        st.session_state.embedder = embedder
        st.session_state.llm = llm
        st.session_state.chat_history = []
        st.session_state.interest_score = 50
        st.session_state.interest_history = [50]
        st.session_state.query_log = []
        st.session_state.order = {}
        st.session_state.app_ready = True

    st.success("✅ All services initialized successfully!")
    st.rerun()

# --- Main UI ---
st.title("🤖 FoodieBot Live Dashboard")
chat_col, analytics_col = st.columns([0.7, 0.3])

render_chat_interface(chat_col)
render_analytics_sidebar(analytics_col)
with st.sidebar:
    render_admin_panel()