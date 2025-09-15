# app.py
import streamlit as st
import os
from database import initialize_services
from bot_logic import initialize_llm
from ui_components import render_chat_interface, render_analytics_sidebar, render_admin_panel

st.set_page_config(
    page_title="FoodieBot Live Demo",
    page_icon="🤖",
    layout="wide",
)
st.markdown("""<style>.main .block-container {padding-top: 1rem;}</style>""", unsafe_allow_html=True)

if "app_ready" not in st.session_state:
    st.info("Initializing services...")
    # Load .env locally if python-dotenv is available; on Streamlit Cloud we rely on Secrets/env vars
    try:
        from dotenv import load_dotenv  # type: ignore
        load_dotenv()
    except Exception:
        st.info("Using environment/Secrets without .env loading (python-dotenv not found).")
    df, collection, embedder = initialize_services()
    llm = initialize_llm()

    if df is None:
        st.error("❌ Failed to load product data. Check CSV file.")
        st.stop()
    if collection is None or embedder is None:
        st.error("❌ Failed to initialize vector database or embeddings.")
        st.stop()
    if llm is None:
        st.error("❌ Failed to initialize LLM. Check GROQ_API_KEY.")
        st.stop()

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
# Main UI 
st.title("🤖 FoodieBot Live Dashboard")
# Two-column layout
chat_column, analytics_column = st.columns([0.7, 0.3])
render_chat_interface(chat_column)
render_analytics_sidebar(analytics_column)
with st.sidebar:
    render_admin_panel()

