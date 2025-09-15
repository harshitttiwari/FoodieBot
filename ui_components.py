# ui_components.py
import streamlit as st
import pandas as pd
import time
from datetime import datetime

# Import logic functions from our modules
from bot_logic import get_ai_response, calculate_interest_score

DATA_FILE_PATH = 'fast_food_products.csv'

def render_chat_interface(container):
    """Renders the main chatbot interface with a fixed 350px scrollable history box."""
    with container:
        st.header("Conversational Agent")

        # Fixed-height scrollable chat history (350px)
        chat_container = st.container(height=350, border=True)
        
        # Initialize chat history with a welcome message if it doesn't exist.
        if "chat_history" not in st.session_state or not st.session_state.chat_history:
            st.session_state.chat_history = [
                {"role": "assistant", "content": "Welcome to FoodieBot! How can I help you with our menu today?"}
            ]

        # Display all past messages from the history inside the scrollable container.
        for message in st.session_state.chat_history:
            with chat_container.chat_message(message["role"]):
                st.markdown(message["content"])
        
    # Handle new user input, which is fixed at the bottom of the column.
        if prompt := st.chat_input("Ask me about the menu..."):
            # Add user message to history and display it immediately.
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with chat_container.chat_message("user"):
                st.markdown(prompt)

            # --- This is the reliable RAG (Retrieval-Augmented Generation) pipeline ---
            with chat_container.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    time.sleep(1) # Consistent 1-second "thinking" delay
                    
                    # 1. RETRIEVE: Search the database for relevant information.
                    start_time = time.time()
                    search_results = st.session_state.collection.query(
                        query_texts=[prompt], n_results=5, include=["metadatas", "distances"]
                    )
                    query_duration = time.time() - start_time
                    
                    # 2. AUGMENT: Build a clean, factual context for the AI.
                    context = "No relevant items found in the menu."
                    if search_results and search_results['metadatas'][0]:
                        def _fmt_price(v):
                            try:
                                return f"${float(v):.2f}"
                            except Exception:
                                return f"${v}" if v not in (None, "", "N/A") else "N/A"

                        context_lines = [
                            "Use only this menu context. Answer in 5-7 concise bullets with clear spacing (e.g., '720 calories').\n"
                        ]
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

                    # 3. GENERATE: Get the final, reliable response from the AI using the clean context.
                    bot_response = get_ai_response(st.session_state.llm, prompt, st.session_state.chat_history, context)
            
            # Add the bot's response to the chat history.
            st.session_state.chat_history.append({"role": "assistant", "content": bot_response})
            
            # Update the analytics state.
            st.session_state.interest_score = calculate_interest_score(prompt, st.session_state.interest_score)
            st.session_state.interest_history.append(st.session_state.interest_score)
            st.session_state.query_log.append({
                "timestamp": datetime.now().strftime("%H:%M:%S"), "user_query": prompt,
                "top_match": search_results['metadatas'][0][0]['name'] if search_results['metadatas'][0] else "N/A",
                "match_score": 1 - search_results['distances'][0][0] if search_results['distances'][0] else 0,
                "duration_ms": round(query_duration * 1000, 2),
            })
            
            # A single, final rerun to display the new messages and update analytics.
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


# import streamlit as st
# import pandas as pd
# import time
# import random
# from datetime import datetime

# # Import logic functions from our modules
# from bot_logic import get_ai_response, calculate_interest_score

# DATA_FILE_PATH = 'fast_food_products.csv'

# def render_chat_interface(container):
#     """Renders the main chatbot interface using a clean, reliable, single-pass logic."""
#     with container:
#         st.header("Conversational Agent")
        
#         # This container will hold the chat messages and will be scrollable.
#         chat_container = st.container(height=450, border=True)
        
#         # Initialize chat history with a welcome message if it doesn't exist.
#         if "chat_history" not in st.session_state or not st.session_state.chat_history:
#             st.session_state.chat_history = [
#                 {"role": "assistant", "content": "Welcome to FoodieBot! How can I help you with our menu today?"}
#             ]

#         # Display all past messages from the history inside the scrollable container.
#         for message in st.session_state.chat_history:
#             with chat_container.chat_message(message["role"]):
#                 st.markdown(message["content"])
        
#         # Handle new user input, which is fixed at the bottom of the column.
#         if prompt := st.chat_input("Ask me about the menu..."):
#             # Add user message to history and display it immediately.
#             st.session_state.chat_history.append({"role": "user", "content": prompt})
#             with chat_container.chat_message("user"):
#                 st.markdown(prompt)

#             # --- This is the reliable RAG (Retrieval-Augmented Generation) pipeline ---
#             with chat_container.chat_message("assistant"):
#                 with st.spinner("Thinking..."):
#                     time.sleep(1) # Consistent 1-second "thinking" delay
                    
#                     # 1. RETRIEVE: Search the database for relevant information.
#                     start_time = time.time()
#                     search_results = st.session_state.collection.query(
#                         query_texts=[prompt], n_results=5, include=["metadatas", "distances"]
#                     )
#                     query_duration = time.time() - start_time
                    
#                     # 2. AUGMENT: Build a clean, factual context for the AI.
#                     context = "No relevant items found in the menu."
#                     if search_results and search_results['metadatas'][0]:
#                         context = "Here is the ONLY relevant information from the menu. Use this and nothing else to answer the user's question:\n"
#                         for meta in search_results['metadatas'][0]:
#                             context += f"- Item: {meta.get('name', 'N/A')}, Price: ${meta.get('price', 'N/A')}, Calories: {meta.get('calories', 'N/A')}, Ingredients: {meta.get('ingredients', 'N/A')}, Allergens: {meta.get('allergens', 'None Listed')}\n"

#                     # 3. GENERATE: Get the final, reliable response from the AI using the clean context.
#                     bot_response = get_ai_response(st.session_state.llm, prompt, st.session_state.chat_history, context)
            
#             # Add the bot's response to the chat history.
#             st.session_state.chat_history.append({"role": "assistant", "content": bot_response})
            
#             # Update the analytics state.
#             st.session_state.interest_score = calculate_interest_score(prompt, st.session_state.interest_score)
#             st.session_state.interest_history.append(st.session_state.interest_score)
#             st.session_state.query_log.append({
#                 "timestamp": datetime.now().strftime("%H:%M:%S"), "user_query": prompt,
#                 "top_match": search_results['metadatas'][0][0]['name'] if search_results['metadatas'][0] else "N/A",
#                 "match_score": 1 - search_results['distances'][0][0] if search_results['distances'][0] else 0,
#                 "duration_ms": round(query_duration * 1000, 2),
#             })
            
#             # A single, final rerun to display the new messages and update analytics.
#             st.rerun()

# def render_analytics_sidebar(container):
#     """Renders the live analytics in the provided sidebar container."""
#     with container:
#         st.header("📈 Live Analytics")
#         st.subheader("Latest Database Query")
#         if not st.session_state.query_log:
#             st.info("No queries yet.")
#         else:
#             latest_query = st.session_state.query_log[-1]
#             st.text(f"User Query: \"{latest_query['user_query']}\"")
#             st.text(f"Top Match: {latest_query['top_match']} ({latest_query['match_score']:.2%})")
#             st.text(f"Query Time: {latest_query['duration_ms']} ms")
        
#         st.markdown("---")
        
#         st.subheader("Interest Score (UI Only)")
#         st.metric("Current Score", f"{st.session_state.interest_score}%")
#         st.line_chart(st.session_state.interest_history)

# def render_admin_panel():
#     """Renders the product database admin panel in the main sidebar."""
#     st.header("⚙️ Admin Panel")
#     st.info("View and edit product data.")
#     edited_df = st.data_editor(
#         st.session_state.df, num_rows="dynamic", use_container_width=True
#     )
#     if st.button("Save Changes to CSV"):
#         try:
#             edited_df.to_csv(DATA_FILE_PATH, index=False)
#             st.success("Changes saved!")
#         except Exception as e:
#             st.error(f"Failed to save: {e}")



