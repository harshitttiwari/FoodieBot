#app.py
import streamlit as st
from dotenv import load_dotenv
import os

# Import functions from our modules
from database import initialize_services
from bot_logic import initialize_llm
from ui_components import render_chat_interface, render_analytics_sidebar, render_admin_panel

# --- Page Configuration ---
st.set_page_config(
    page_title="FoodieBot Live Demo",
    page_icon="🤖",
    layout="wide",
)

# This custom CSS removes the excessive top padding for a cleaner, more professional look.
st.markdown("""<style>.main .block-container {padding-top: 1rem;}</style>""", unsafe_allow_html=True)

# --- App State Initialization (runs only once) ---
if "app_ready" not in st.session_state:
    st.info("Initializing services...")
    load_dotenv()
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    if not GROQ_API_KEY or GROQ_API_KEY == "your-groq-api-key-here":
        st.error("GROQ_API_KEY not found. Please set it in your .env file.")
        st.stop()

    df, collection, embedder = initialize_services()
    llm = initialize_llm()

    if all((df is not None, collection is not None, embedder is not None, llm is not None)):
        st.success("All services initialized successfully!")
        
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
        st.rerun()
    else:
        st.error("A critical service failed to initialize. Please check the terminal for errors.")
        st.stop()

# --- Main UI Rendering ---
st.title("🤖 FoodieBot Live Dashboard")

# Create the definitive 70/30 two-column layout
chat_column, analytics_column = st.columns([0.7, 0.3])

# Render the UI components into their respective columns
render_chat_interface(chat_column)
render_analytics_sidebar(analytics_column)

# The admin panel remains in the main sidebar
with st.sidebar:
    render_admin_panel()
