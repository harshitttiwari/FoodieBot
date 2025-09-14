# botlogic.py
import streamlit as st
from langchain_groq import ChatGroq

@st.cache_resource
def initialize_llm():
    """Initializes the Groq Large Language Model."""
    try:
        # Using the faster, more efficient model for real-time chat.
        # Temperature is lowered to make the bot more factual and less creative (prevents hallucination).
        llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.2)
        return llm
    except Exception as e:
        st.error(f"Failed to initialize the Language Model: {e}")
        return None

def get_ai_response(llm, user_input, chat_history, context):
    """Generates a reliable, professional response from the LLM."""
    
    # Check for inappropriate or irrelevant content first
    if _is_inappropriate_or_irrelevant(user_input):
        return "My apologies, but I can only provide information about our menu items."
    
    # Handle simple conversational responses
    user_lower = user_input.lower().strip()
    
    # Handle negative responses
    if user_lower in ['no', 'nothing', 'nope', 'nah']:
        return "No problem! If you change your mind or have any questions about our menu, just let me know."
    
    # Handle exit/goodbye
    if user_lower in ['exit', 'bye', 'goodbye', 'quit', 'leave']:
        return "Thank you for visiting! Have a great day!"
    
    # Handle yes without context
    if user_lower in ['yes', 'yeah', 'yep', 'ok', 'okay']:
        return "Great! What would you like to know about our menu?"
    
    # Convert chat history to a readable string for the prompt.
    history_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history])

    # Enhanced prompt with stricter guardrails
    prompt = f"""
    You are FoodieBot, a professional restaurant assistant. Follow these STRICT rules:

    **ABSOLUTE REQUIREMENTS:**
    1. **NO INTERNAL MONOLOGUE:** NEVER use phrases like "Based on your requirements", "I would recommend", "I'll exclude", or any self-correction text. Your responses must be direct and natural.
    2. **ALLERGEN SAFETY:** If a customer mentions an allergy (like "no soy"), you MUST check allergen information carefully. NEVER recommend items that contain even trace amounts of that allergen.
    3. **FOOD CLASSIFICATION:** Understand the difference between appetizers/snacks (chips, poppers) and main dishes (burgers, pizza, bowls). When someone asks for a "dish" or "meal", recommend substantial items, not snacks.
    4. **NO HALLUCINATION:** Only use information from the CONTEXT. If information isn't available, say "I don't have that information."
    5. **STAY ON TOPIC:** Only discuss menu items. For anything else, respond: "My apologies, but I can only provide information about our menu items."
    6. **FORMATTING:** When listing multiple items, use bullet points (•) for better readability.
    7. **SMART SUGGESTIONS:** If customer orders spicy food (spice level 6+), automatically suggest cooling drinks like lemonades or smoothies.
    8. **PRICING:** Always format prices clearly as $X.XX without any extra characters.

    **CONTEXT:**
    {context}

    **CONVERSATION HISTORY:**
    {history_str}

    **USER MESSAGE:** {user_input}

    Respond as FoodieBot (naturally, no meta-commentary):
    """
    try:
        response = llm.invoke(prompt)
        
        # Post-process to catch any remaining internal monologue
        cleaned_response = _clean_response(response.content)
        
        # Auto-suggest drinks for spicy food orders
        if any(spicy_item in user_input.lower() for spicy_item in ['ghost pepper', 'spicy', 'hot', 'jalapeño', 'buffalo', 'sriracha']):
            if 'add' in user_input.lower() or 'order' in user_input.lower():
                cleaned_response += "\n\nSince you ordered something spicy, would you like a cooling drink? I recommend our Mango Citrus Refresher or Strawberry Basil Lemonade to balance the heat!"
        
        return cleaned_response
    except Exception as e:
        return f"Sorry, I'm having a technical issue and can't respond right now. Error: {e}"

def _is_inappropriate_or_irrelevant(user_input):
    """Simple check for obvious inappropriate content or gibberish."""
    
    # Check for gibberish (too many consonants in a row)
    if len(user_input) > 4:
        # Simple gibberish detection - if we find 5+ consonants in a row, it's probably gibberish
        import re
        consonant_clusters = re.findall(r'[bcdfghjklmnpqrstvwxyz]{5,}', user_input.lower())
        if consonant_clusters:
            return True
    
    # Check for obvious inappropriate words
    bad_words = ['sex', 'porn', 'fuck', 'shit']
    for word in bad_words:
        if word in user_input.lower():
            return True
    
    # Check for completely unrelated topics (only if NO food words present)
    if 'weather' in user_input.lower() or 'politics' in user_input.lower():
        # But allow if they mention food too
        food_words = ['food', 'eat', 'menu', 'hungry', 'burger', 'pizza', 'order']
        has_food_context = any(word in user_input.lower() for word in food_words)
        if not has_food_context:
            return True
    
    return False

def _clean_response(response):
    """Simple cleanup to remove obvious internal monologue."""
    # Remove obvious internal monologue phrases
    phrases_to_remove = [
        "Based on your requirements",
        "Based on your request", 
        "I would recommend",
        "I'll exclude",
        "Looking at the menu"
    ]
    
    for phrase in phrases_to_remove:
        if phrase in response:
            # Simple replacement - remove the sentence containing this phrase
            sentences = response.split('.')
            clean_sentences = []
            for sentence in sentences:
                if phrase not in sentence:
                    clean_sentences.append(sentence)
            response = '.'.join(clean_sentences)
    
    return response.strip()

# This is a simplified version for the UI only. It does not control the bot's logic.
def calculate_interest_score(user_input, current_score):
    """Calculates a display score for the UI based on user input keywords."""
    score = current_score
    
    # Big boost for actual orders and strong interest
    if any(word in user_input.lower() for word in ["add it", "order it", "i'll take", "yes add", "place order"]):
        score += 25  # Big boost for confirmed orders
    elif any(word in user_input.lower() for word in ["add", "order", "want", "get", "take"]):
        score += 15  # Medium boost for interest
    elif any(word in user_input.lower() for word in ["perfect", "awesome", "love", "great", "excellent", "good"]):
        score += 12  # Positive sentiment
    elif any(word in user_input.lower() for word in ["hungry", "starving", "craving"]):
        score += 10  # Hunger indicators
    
    # Negative adjustments
    if any(word in user_input.lower() for word in ["no", "not interested", "don't want", "different", "exit"]):
        score -= 8
    
    return max(0, min(100, score))
