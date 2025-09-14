# ui_components.py
import streamlit as st
import pandas as pd
import time
import random
from datetime import datetime

# Import logic functions from our modules
from bot_logic import get_ai_response, calculate_interest_score

DATA_FILE_PATH = 'fast_food_products.csv'

def _build_enhanced_context(user_query, search_results):
    """Build enhanced context with allergen filtering and better categorization."""
    import re
    
    if not search_results or not search_results['metadatas'][0]:
        return "No relevant items found in the menu."
    
    # Detect allergen restrictions from user query
    allergen_restrictions = _detect_allergen_restrictions(user_query)
    
    # Detect dietary preferences and request type
    request_type = _analyze_request_type(user_query)
    
    # Filter and categorize items
    filtered_items = _filter_items_by_restrictions(search_results['metadatas'][0], allergen_restrictions)
    categorized_items = _categorize_items(filtered_items, request_type)
    
    # Build context string
    if not filtered_items:
        allergen_msg = f" (avoiding {', '.join(allergen_restrictions)})" if allergen_restrictions else ""
        return f"No suitable menu items found{allergen_msg}. This may be due to allergen restrictions or the specific request."
    
    context = "Here are the relevant menu items that match your request:\n\n"
    
    # Add items by category with clear distinctions
    for category, items in categorized_items.items():
        if items:
            context += f"**{category.upper()}:**\n"
            for item in items:
                allergen_info = item.get('allergens', 'None listed')
                if allergen_info == 'None listed' or allergen_info == '':
                    allergen_display = "No allergens listed"
                else:
                    allergen_display = f"Contains: {allergen_info}"
                
                context += f"- {item.get('name', 'N/A')} (${item.get('price', 'N/A')})\n"
                context += f"  Ingredients: {item.get('ingredients', 'N/A')}\n"
                context += f"  Allergens: {allergen_display}\n"
                context += f"  Category: {item.get('category', 'N/A')}\n"
                if item.get('calories') and item.get('calories') != 'N/A':
                    context += f"  Calories: {item.get('calories')}\n"
                context += "\n"
    
    return context

def _detect_allergen_restrictions(user_query):
    """Detect allergen restrictions mentioned in user query."""
    restrictions = []
    query_lower = user_query.lower()
    
    # Enhanced allergen detection patterns
    allergen_patterns = {
        'soy': [
            'no soy', 'without soy', 'soy free', 'soy-free', 'soy allergy', 
            'absolutely no soy', 'avoid soy', 'allergic to soy'
        ],
        'gluten': [
            'no gluten', 'gluten free', 'gluten-free', 'celiac', 'gluten allergy',
            'without gluten', 'avoid gluten'
        ],
        'dairy': [
            'no dairy', 'dairy free', 'dairy-free', 'lactose intolerant', 
            'milk allergy', 'without dairy', 'avoid dairy'
        ],
        'nuts': [
            'no nuts', 'nut free', 'nut-free', 'nut allergy', 'tree nut allergy',
            'peanut allergy', 'without nuts', 'avoid nuts'
        ],
        'egg': [
            'no egg', 'egg free', 'egg-free', 'egg allergy', 'without eggs',
            'avoid eggs'
        ],
        'fish': [
            'no fish', 'fish free', 'fish-free', 'fish allergy', 'seafood allergy',
            'without fish', 'avoid fish'
        ],
        'sesame': [
            'no sesame', 'sesame free', 'sesame-free', 'sesame allergy',
            'without sesame', 'avoid sesame'
        ]
    }
    
    for allergen, patterns in allergen_patterns.items():
        for pattern in patterns:
            if pattern in query_lower:
                restrictions.append(allergen)
                break
    
    return list(set(restrictions))  # Remove duplicates

def _analyze_request_type(user_query):
    """Analyze what type of food the user is requesting."""
    query_lower = user_query.lower()
    
    request_types = {
        'main_dish': ['dish', 'meal', 'dinner', 'lunch', 'entree', 'main', 'hungry', 'filling'],
        'savory': ['savory', 'salty', 'not sweet', 'savoury'],
        'sweet': ['sweet', 'dessert', 'sugar'],
        'snack': ['snack', 'appetizer', 'light', 'small'],
        'drink': ['drink', 'beverage', 'thirsty']
    }
    
    detected_types = []
    for req_type, keywords in request_types.items():
        if any(keyword in query_lower for keyword in keywords):
            detected_types.append(req_type)
    
    return detected_types

def _filter_items_by_restrictions(items, allergen_restrictions):
    """Filter items based on allergen restrictions."""
    if not allergen_restrictions:
        return items
    
    filtered_items = []
    for item in items:
        allergens = item.get('allergens', '').lower()
        
        # Check if any restricted allergen is present (including trace amounts)
        safe_item = True
        for restriction in allergen_restrictions:
            if restriction in allergens or f"{restriction} (trace)" in allergens:
                safe_item = False
                break
        
        if safe_item:
            filtered_items.append(item)
    
    return filtered_items

def _categorize_items(items, request_types):
    """Categorize items based on request type and food category."""
    categories = {
        'main_dishes': [],
        'appetizers_snacks': [],
        'beverages': [],
        'desserts': []
    }
    
    for item in items:
        category = item.get('category', '').lower()
        name = item.get('name', '').lower()
        
        # Categorize based on menu category
        if category in ['burgers', 'pizza', 'tacos & wraps', 'salads & healthy options', 'breakfast items']:
            categories['main_dishes'].append(item)
        elif category in ['sides & appetizers', 'fried chicken']:
            # For fried chicken, distinguish between main items and snacks
            if 'bites' in name or 'poppers' in name or 'tots' in name:
                categories['appetizers_snacks'].append(item)
            else:
                categories['main_dishes'].append(item)
        elif category == 'beverages':
            categories['beverages'].append(item)
        elif category == 'desserts':
            categories['desserts'].append(item)
        else:
            # Default categorization
            if any(word in name for word in ['chips', 'fries', 'rings', 'bites', 'poppers']):
                categories['appetizers_snacks'].append(item)
            else:
                categories['main_dishes'].append(item)
    
    # If user specifically asked for main dishes, prioritize those
    if 'main_dish' in request_types:
        return {'main_dishes': categories['main_dishes']}
    elif 'snack' in request_types:
        return {'appetizers_snacks': categories['appetizers_snacks']}
    elif 'drink' in request_types:
        return {'beverages': categories['beverages']}
    
    return categories

def render_chat_interface(container):
    """Renders the main chatbot interface using a clean, reliable, single-pass logic."""
    with container:
        st.header("Conversational Agent")
        
        # This container will hold the chat messages and will be scrollable.
        chat_container = st.container(height=450, border=True)
        
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

            # --- Enhanced RAG (Retrieval-Augmented Generation) pipeline ---
            with chat_container.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    time.sleep(1) # Consistent 1-second "thinking" delay
                    
                    # 1. RETRIEVE: Search the database for relevant information.
                    start_time = time.time()
                    search_results = st.session_state.collection.query(
                        query_texts=[prompt], n_results=10, include=["metadatas", "distances"]
                    )
                    query_duration = time.time() - start_time
                    
                    # 2. ENHANCE: Apply intelligent filtering and context building
                    context = _build_enhanced_context(prompt, search_results)

                    # 3. GENERATE: Get the final, reliable response from the AI using the enhanced context.
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
        st.session_state.df, num_rows="dynamic", use_container_width=True
    )
    if st.button("Save Changes to CSV"):
        try:
            edited_df.to_csv(DATA_FILE_PATH, index=False)
            st.success("Changes saved!")
        except Exception as e:
            st.error(f"Failed to save: {e}")
