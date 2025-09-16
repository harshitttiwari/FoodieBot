# ui_components.py

import streamlit as st
import pandas as pd
import time
from datetime import datetime
import os  # <-- Import the 'os' module

# Import logic functions from our modules
from bot_logic import get_ai_response, calculate_interest_score

# --- FIX: Create a reliable path to the CSV file ---
# Get the directory where this script (ui_components.py) is located
script_dir = os.path.dirname(__file__)
# Join that directory with the filename to create a full path
DATA_FILE_PATH = os.path.join(script_dir, "fast_food_products.csv")


def render_chat_interface(container):
    """Renders the main chatbot interface with a fixed 350px scrollable history box."""
    with container:
        st.header("Conversational Agent")
        chat_container = st.container(height=350, border=True)

        if "chat_history" not in st.session_state or not st.session_state.chat_history:
            st.session_state.chat_history = [
                {"role": "assistant", "content": "Welcome to FoodieBot! How can I help you with our menu today?"}
            ]

        for message in st.session_state.chat_history:
            with chat_container.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Ask me about the menu..."):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with chat_container.chat_message("user"):
                st.markdown(prompt)

            with chat_container.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    time.sleep(1)

                    start_time = time.time()
                    search_results = st.session_state.collection.query(
                        query_texts=[prompt], n_results=5, include=["metadatas", "distances"]
                    )
                    query_duration = time.time() - start_time

                    context = "No relevant items found in the menu."
                    if search_results and search_results['metadatas'][0]:
                        def _fmt_price(v):
                            try: return f"${float(v):.2f}"
                            except Exception: return f"${v}" if v not in (None, "", "N/A") else "N/A"

                        context_lines = ["Use only this menu context. Answer in 5-7 concise bullets with clear spacing (e.g., '720 calories').\n"]
                        for meta in search_results['metadatas'][0]:
                            name = meta.get('name', 'N/A')
                            price = _fmt_price(meta.get('price', 'N/A'))
                            calories = meta.get('calories', 'N/A')
                            ingredients = str(meta.get('ingredients', 'N/A')).replace(';', ', ')
                            allergens = str(meta.get('allergens', 'None Listed')).replace(';', ', ')
                            context_lines.append(
                                f"- Item: {name}; Price: {price}; Calories: {calories}; Ingredients: {ingredients}; Allergens: {allergens}"
                            )
                        context = "\n".join(context_lines)

                    bot_response = get_ai_response(st.session_state.llm, prompt, st.session_state.chat_history, context)

            st.session_state.chat_history.append({"role": "assistant", "content": bot_response})
            st.session_state.interest_score = calculate_interest_score(prompt, st.session_state.interest_score)
            st.session_state.interest_history.append(st.session_state.interest_score)
            st.session_state.query_log.append({
                "timestamp": datetime.now().strftime("%H:%M:%S"), "user_query": prompt,
                "top_match": search_results['metadatas'][0][0]['name'] if search_results['metadatas'][0] else "N/A",
                "match_score": 1 - search_results['distances'][0][0] if search_results['distances'][0] else 0,
                "duration_ms": round(query_duration * 1000, 2),
            })
            st.rerun()

def render_analytics_sidebar(container):
    """Renders the live analytics in the provided sidebar container."""
    with container:
        st.header("📈 Live Analytics")
        st.subheader("Latest Database Query")
        if not st.session_state.query_log:
            st.info("No queries yet.")
        else:
            latest_query = st.session_state.query_log[-1]
            st.text(f"User Query: \"{latest_query['user_query']}\"")
            st.text(f"Top Match: {latest_query['top_match']} ({latest_query['match_score']:.2%})")
            st.text(f"Query Time: {latest_query['duration_ms']} ms")
        st.markdown("---")
        st.subheader("Interest Score (UI Only)")
        st.metric("Current Score", f"{st.session_state.interest_score}%")
        st.line_chart(st.session_state.interest_history)

def render_admin_panel():
    """Renders the product database admin panel in the main sidebar."""
    st.header("⚙️ Admin Panel")
    st.info("View and edit product data.")
    edited_df = st.data_editor(
        st.session_state.df, num_rows="dynamic", width='stretch'
    )
    if st.button("Save Changes to CSV"):
        try:
            edited_df.to_csv(DATA_FILE_PATH, index=False)
            st.success("Changes saved!")
        except Exception as e:
            st.error(f"Failed to save: {e}")