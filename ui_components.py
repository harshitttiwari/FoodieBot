import streamlit as st
import time
from datetime import datetime
from bot_logic import get_ai_response, calculate_interest_score

DATA_FILE_PATH = "fast_food_products.csv"

# ----------------- Context Building Helpers -----------------
def _build_enhanced_context(user_query, search_results):
    """Build readable context for the LLM from database search results."""
    if not search_results or not search_results.get("metadatas") or not search_results["metadatas"][0]:
        return "No relevant items found in the menu."

    allergen_restrictions = _detect_allergen_restrictions(user_query)
    request_type = _analyze_request_type(user_query)

    filtered_items = _filter_items_by_restrictions(search_results["metadatas"][0], allergen_restrictions)
    categorized_items = _categorize_items(filtered_items, request_type)

    if not filtered_items:
        allergen_msg = f" (avoiding {', '.join(allergen_restrictions)})" if allergen_restrictions else ""
        return f"No suitable menu items found{allergen_msg}."

    # Limit items per category to keep responses concise and avoid repetition
    MAX_PER_CATEGORY = 3
    context = "Here are the relevant menu items:\n\n"
    for category, items in categorized_items.items():
        if not items:
            continue
        context += f"**{category.upper()}:**\n"
        for item in items[:MAX_PER_CATEGORY]:
            price = _format_price(item.get("price"))
            allergens = item.get("allergens", "None listed") or "None listed"
            allergens_display = "No allergens listed" if allergens == "None listed" else f"Contains: {allergens}"
            ingredients = (item.get("ingredients") or "N/A").replace(";", ", ")

            context += f"• {item.get('name','N/A')} ({price})\n"
            context += f"  Ingredients: {ingredients}\n"
            context += f"  Allergens: {allergens_display}\n"
            context += f"  Category: {item.get('category','N/A')}\n"
            if item.get("calories") and item.get("calories") != "N/A":
                context += f"  Calories: {item['calories']}\n"
            context += "\n"
    # Brief prompt hint to encourage concise answers
    context += "Please answer concisely in 5-7 bullet points."
    return context

def _format_price(value):
    try:
        return f"${float(value):.2f}"
    except Exception:
        return "Price N/A"

def _detect_allergen_restrictions(user_query):
    query = user_query.lower()
    allergen_keywords = {
        "soy": ["no soy", "soy free", "soy allergy"],
        "gluten": ["gluten free", "celiac"],
        "dairy": ["dairy free", "lactose", "milk allergy"],
        "nuts": ["nut free", "peanut allergy", "tree nut allergy"],
        "egg": ["no egg", "egg free"],
        "fish": ["no fish", "fish free", "seafood allergy"],
        "sesame": ["no sesame", "sesame free"]
    }
    return [a for a, kws in allergen_keywords.items() if any(k in query for k in kws)]

def _analyze_request_type(user_query):
    query = user_query.lower()
    keywords = {
        "main_dish": ["meal", "dish", "dinner", "lunch"],
        "snack": ["snack", "appetizer", "light"],
        "drink": ["drink", "beverage", "thirsty"],
        "sweet": ["sweet", "dessert"],
    }
    return [t for t, kws in keywords.items() if any(k in query for k in kws)]

def _filter_items_by_restrictions(items, restrictions):
    if not restrictions:
        return items
    safe_items = []
    for item in items:
        allergens = (item.get("allergens") or "").lower()
        if not any(r in allergens for r in restrictions):
            safe_items.append(item)
    return safe_items

def _categorize_items(items, request_types):
    categories = {"main_dishes": [], "appetizers_snacks": [], "beverages": [], "desserts": []}
    for item in items:
        cat = (item.get("category") or "").lower()
        name = (item.get("name") or "").lower()
        if cat in ["burgers", "pizza", "tacos & wraps", "salads", "breakfast items"]:
            categories["main_dishes"].append(item)
        elif cat in ["sides & appetizers", "fried chicken"] or any(x in name for x in ["fries", "chips", "bites"]):
            categories["appetizers_snacks"].append(item)
        elif cat == "beverages":
            categories["beverages"].append(item)
        elif cat == "desserts":
            categories["desserts"].append(item)
    if "main_dish" in request_types: return {"main_dishes": categories["main_dishes"]}
    if "snack" in request_types: return {"appetizers_snacks": categories["appetizers_snacks"]}
    if "drink" in request_types: return {"beverages": categories["beverages"]}
    return categories

# ----------------- UI Rendering -----------------
def render_chat_interface(container):
    """Chatbot interface with fixed rectangle and scrollable history."""
    with container:
        st.header("Conversational Agent")
        # Removed the empty HTML chatbox that caused a big white rectangle.
        # We rely on Streamlit's native chat_message bubbles. If you later
        # want a fixed-height scroll area (~350px), we can add a small CSS
        # override that limits the chat history block height.

        # Display chat history
        chat_container = st.container()
        for msg in st.session_state.chat_history:
            with chat_container.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # User input
        if prompt := st.chat_input("Ask me about the menu..."):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with chat_container.chat_message("user"): st.markdown(prompt)

            with chat_container.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    start = time.time()
                    search_results = st.session_state.collection.query(
                        query_texts=[prompt], n_results=10, include=["metadatas", "distances"]
                    )
                    duration = time.time() - start

                    context = _build_enhanced_context(prompt, search_results)
                    response = get_ai_response(st.session_state.llm, prompt, st.session_state.chat_history, context)
                st.markdown(response)

            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.session_state.interest_score = calculate_interest_score(prompt, st.session_state.interest_score)
            st.session_state.interest_history.append(st.session_state.interest_score)
            st.session_state.query_log.append({
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "user_query": prompt,
                "top_match": search_results["metadatas"][0][0]["name"] if search_results["metadatas"][0] else "N/A",
                "match_score": 1 - search_results["distances"][0][0] if search_results["distances"][0] else 0,
                "duration_ms": round(duration * 1000, 2),
            })

def render_analytics_sidebar(container):
    with container:
        st.header("📈 Live Analytics")
        if not st.session_state.query_log:
            st.info("No queries yet.")
            return
        latest = st.session_state.query_log[-1]
        st.subheader("Latest Query")
        st.text(f"User Query: {latest['user_query']}")
        st.text(f"Top Match: {latest['top_match']} ({latest['match_score']:.2%})")
        st.text(f"Time: {latest['duration_ms']} ms")

        st.subheader("Interest Score")
        st.metric("Current", f"{st.session_state.interest_score}%")
        st.line_chart(st.session_state.interest_history)

def render_admin_panel():
    st.header("⚙️ Admin Panel")
    df = st.data_editor(st.session_state.df, num_rows="dynamic", width='stretch')
    if st.button("Save to CSV"):
        try:
            df.to_csv(DATA_FILE_PATH, index=False)
            st.success("Changes saved!")
        except Exception as e:
            st.error(f"Save failed: {e}")
