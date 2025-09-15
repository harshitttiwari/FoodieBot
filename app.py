import streamlit as st
import os
from database import initialize_services
from bot_logic import initialize_llm
from ui_components import render_chat_interface, render_analytics_sidebar, render_admin_panel

# --- Page Config ---
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
    /* Keep chat area visually compact on small screens (~350px tall history) */
    .stChatMessage {max-height: 350px; overflow-y: auto;}
    </style>
    """,
    unsafe_allow_html=True
)

# --- Init Phase ---
if "app_ready" not in st.session_state:
    st.info("🚀 Initializing services...")

    # Load .env (local dev only)
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        st.info("⚠️ Skipping .env loading (likely running on Hugging Face Spaces).")

    # Ensure embedding cache is writable for HuggingFace transformers
    os.environ["HF_HOME"] = "/tmp/hf_cache"
    os.environ["TRANSFORMERS_CACHE"] = "/tmp/hf_cache"

    # Ensure ONNX MiniLM embeddings can download to writable folder
    from chromadb.utils import embedding_functions
    onnx_model_path = "/tmp/onnx_model"
    os.makedirs(onnx_model_path, exist_ok=True)
    embedding_functions.ONNXMiniLM_L6_V2.DOWNLOAD_PATH = onnx_model_path

    # Initialize services
    df, collection, embedder = initialize_services()
    llm = initialize_llm()

    # Check services
    if df is None:
        st.error("❌ Failed to load product data. Ensure `fast_food_products.csv` exists in the root folder.")
        st.stop()
    if collection is None or embedder is None:
        st.error("❌ Failed to initialize vector DB or embeddings.")
        st.stop()
    if llm is None:
        st.error("❌ Failed to initialize LLM. Check GROQ_API_KEY.")
        st.stop()

    # Save to session
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
