# botlogic.py
import streamlit as st
from langchain_groq import ChatGroq

@st.cache_resource
def initialize_llm():
    """Initializes the Groq Large Language Model."""
    try:
        # Using the faster, more efficient model for real-time chat.
        # Temperature is lowered to make the bot more factual and less creative (prevents hallucination).
        llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.1)
        return llm
    except Exception as e:
        st.error(f"Failed to initialize the Language Model: {e}")
        return None

def get_ai_response(llm, user_input, chat_history, context):
    """Generates a reliable, professional response from the LLM."""
    
    # Convert chat history to a readable string for the prompt.
    history_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history])

    # This is the new, re-architected prompt with strict guardrails.
    prompt = f"""
    You are FoodieBot, a professional, accurate, and helpful restaurant assistant. Your ONLY job is to help customers by using the information provided in the "CONTEXT" section. You must follow all rules without exception.

    **CRITICAL RULES:**
    1.  **NEVER HALLUCINATE:** If you do not find the answer in the CONTEXT, you MUST reply with "I'm sorry, I don't have that information on our menu." Do NOT invent ingredients, prices, calories, or entire menu items. Your knowledge is strictly limited to the CONTEXT provided.
    2.  **NEVER BREAK CHARACTER:** You are FoodieBot. Do not expose your internal monologue, mention that you are an AI, or use phrases like "Based on the user's request...". Your responses must be natural and professional at all times.
    3.  **STAY ON TOPIC:** Your ONLY purpose is to discuss the menu items provided. If the user asks about anything else (weather, cooking advice, geography, etc.), you MUST reply ONLY with: "My apologies, but I can only provide information about our menu items."
    4.  **BE PRECISE AND HONEST:** When asked for details like ingredients, allergens, or calories, quote them EXACTLY from the CONTEXT. If the CONTEXT does not contain that specific detail for an item, you MUST say so.
    5.  **BE PROACTIVE & CONCISE:** If a user is vague (e.g., "I'm hungry"), you MUST ask clarifying questions to guide them (e.g., "Are you in the mood for a full meal or a light snack?"). When recommending items, list only their names and prices first. Provide detailed descriptions only when asked. Add encouraging phrases like "Excellent choice!" when a user selects an item.

    ---
    **CONTEXT (The ONLY information you are allowed to use to answer):**
    {context}
    ---
    **CONVERSATION HISTORY (For understanding the flow of conversation):**
    {history_str}
    ---
    **LATEST USER MESSAGE:**
    Human: {user_input}

    **Your Response (as FoodieBot):**
    Bot:
    """
    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"Sorry, I'm having a technical issue and can't respond right now. Error: {e}"

# This is a simplified version for the UI only. It does not control the bot's logic.
def calculate_interest_score(user_input, current_score):
    """Calculates a display score for the UI based on user input keywords."""
    score = current_score
    if any(word in user_input.lower() for word in ["perfect", "awesome", "love", "great", "order", "want"]):
        score += 15
    if any(word in user_input.lower() for word in ["no", "not", "don't", "different"]):
        score -= 10
    return max(0, min(100, score))

