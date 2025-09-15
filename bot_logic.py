# bot_logic.py
import os
import streamlit as st
from langchain_groq import ChatGroq

@st.cache_resource
def initialize_llm():
    """Initializes the Groq Large Language Model with API key."""
    # Prefer environment variable; fall back to Streamlit Secrets when running on Streamlit Cloud
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        try:
            # st.secrets is only available in Streamlit runtime; .get for graceful access
            api_key = st.secrets.get("GROQ_API_KEY")  # type: ignore[attr-defined]
        except Exception:
            api_key = None

    if not api_key:
        st.error(
            "❌ GROQ_API_KEY not found. Set it in a local .env file or in Streamlit Cloud Secrets (GROQ_API_KEY)."
        )
        return None
    try:
        llm = ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0.2,
            api_key=api_key
        )
        return llm
    except Exception as e:
        st.error(f"❌ Failed to initialize the Language Model: {e}")
        return None


def get_ai_response(llm, user_input, chat_history, context):
    """Generates a professional FoodieBot response using the LLM."""
    if not llm:
        return "The language model is not available. Please try again later."

    if _is_inappropriate_or_irrelevant(user_input):
        return "My apologies, but I can only provide information about our menu items."

    history_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history])
    prompt = f"""
    You are FoodieBot, a professional restaurant assistant. Follow these rules:
    - NEVER use internal reasoning phrases.
    - Respect allergens: exclude items with allergens mentioned by user.
    - Classify food correctly (main dish vs snack).
    - Only provide information from CONTEXT; if unknown, say "I don't have that information."
    - Use bullets (•), show prices as $X.XX, include calories, category, allergens if known.
    - Suggest cooling drinks if user orders spicy food.
    - Keep responses natural, concise, and helpful.

    CONTEXT:
    {context}

    CONVERSATION HISTORY:
    {history_str}

    USER MESSAGE:
    {user_input}

    Respond as FoodieBot.
    """
    try:
        response = llm.invoke(prompt)
        cleaned_response = _clean_response(response.content)

        # Suggest cooling drinks if user mentioned spicy items
        spicy_keywords = ['ghost pepper', 'spicy', 'hot', 'jalapeño', 'buffalo', 'sriracha']
        if any(word in user_input.lower() for word in spicy_keywords):
            if any(word in user_input.lower() for word in ['add', 'order']):
                cleaned_response += "\n\nSince you ordered something spicy, would you like a cooling drink? I recommend our Mango Citrus Refresher or Strawberry Basil Lemonade!"

        return cleaned_response
    except Exception as e:
        return f"Sorry, I'm having a technical issue and can't respond right now. Error: {e}"


def _is_inappropriate_or_irrelevant(user_input):
    """Checks for inappropriate content or off-topic messages."""
    bad_words = ['sex', 'porn', 'fuck', 'shit']
    if any(word in user_input.lower() for word in bad_words):
        return True

    if len(user_input) > 10:
        non_ascii_count = sum(1 for c in user_input if ord(c) > 127)
        if non_ascii_count > len(user_input) * 0.7:
            return True

    off_topic = ['weather', 'politics']
    if any(word in user_input.lower() for word in off_topic):
        food_words = ['food', 'eat', 'menu', 'hungry', 'burger', 'pizza', 'order']
        if not any(word in user_input.lower() for word in food_words):
            return True

    return False

def _clean_response(response):
    """Removes phrases related to internal reasoning for clean bot output."""
    phrases_to_remove = [
        "Based on your requirements",
        "Based on your request",
        "I would recommend",
        "I'll exclude",
        "Looking at the menu"
    ]
    for phrase in phrases_to_remove:
        response = response.replace(phrase, "")
    return response.strip()

def calculate_interest_score(user_input, current_score):
    """Calculates a simple interest score based on user keywords."""
    score = current_score
    keywords_boost = {
        25: ["add it", "order it", "i'll take", "yes add", "place order"],
        15: ["add", "order", "want", "get", "take"],
        12: ["perfect", "awesome", "love", "great", "excellent", "good"],
        10: ["hungry", "starving", "craving"],
        -8: ["no", "not interested", "don't want", "different", "exit"]
    }
    for boost, words in keywords_boost.items():
        if any(word in user_input.lower() for word in words):
            score += boost
            break
    return max(0, min(100, score))
