# 🤖 FoodieBot - AI Restaurant Assistant

A Streamlit-based conversational assistant that helps customers explore your menu, powered by Groq’s LLM with a RAG pipeline on ChromaDB. It supports allergen safety, clean formatting, live analytics, and an admin panel to edit the menu.

## ✨ What’s in this version

- ✅ Immediate reply rendering: the assistant response is shown instantly after each question (no “shows on next message” delay)
- ✅ Bullet-point menus with consistent price formatting ($X.XX)
- ✅ Allergen-aware context: filters items based on user’s restrictions
- ✅ Clear categorization: main dishes, snacks, beverages, desserts
- ✅ Live analytics: latest query, timing, similarity score, and interest score trend
- ✅ Admin panel: edit and save the CSV directly from the UI

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- A Groq API key

### Install dependencies
```powershell
pip install streamlit langchain-groq pandas chromadb sentence-transformers python-dotenv
```

### Configure the API key
Create a `.env` file in the project root:
```env
GROQ_API_KEY=your-groq-api-key-here
```

### Run the app
```powershell
streamlit run app.py
```

Open your browser to http://localhost:8501

## 📁 Project Structure (current)

```
FoodieBot/
├── app.py                  # App entry; sets up services, layout, pages
├── bot_logic.py            # LLM prompt, safety filters, response cleaning
├── ui_components.py        # Chat interface, analytics sidebar, admin panel
├── database.py             # CSV load, ChromaDB collection, embeddings
├── fast_food_products.csv  # Menu data
├── advanced_test_suite.py  # Comprehensive quality tests (optional)
└── README.md               # This file
```

## 🧠 Architecture & Flow

### 1) Data & Search (database.py)
- `initialize_services()`
   - Loads `fast_food_products.csv`
   - Normalizes columns and ensures numeric prices
   - Builds a ChromaDB collection with embeddings using `SentenceTransformer('all-MiniLM-L6-v2')`
   - Documents include name, description, ingredients, calories, allergens, dietary tags

### 2) LLM (bot_logic.py)
- `initialize_llm()` uses `GROQ_API_KEY` and `ChatGroq(model='llama-3.1-8b-instant', temperature=0.2)`
- `get_ai_response(llm, user_input, chat_history, context)`
   - Builds a concise prompt with requirements:
      - Use bullets (•), include prices as $X.XX
      - Stay on menu; avoid internal monologue
      - Respect allergen restrictions mentioned by the user
   - Cleans responses via `_clean_response()` (removes phrases like “Based on your request”)
   - Suggests cooling drinks if the user orders spicy items

### 3) Context Building (ui_components.py)
- `_build_enhanced_context(query, search_results)`
   - Detects allergen restrictions and request type
   - Filters items that include restricted allergens
   - Categorizes into: main_dishes, appetizers_snacks, beverages, desserts
   - Formats output:
      - Bullet “• {name} ({$price})”
      - Ingredients (semicolon → comma)
      - Allergens (e.g., “Contains: dairy; gluten” or “No allergens listed”)
      - Category and Calories

### 4) Chat UI (ui_components.py)
- `render_chat_interface()`
   - Renders existing history
   - On new input:
      - Appends the user message to history
      - Queries vector DB and builds context
      - Calls `get_ai_response(...)`
      - Renders the assistant reply immediately with `st.markdown(response)` inside the assistant `chat_message` block
      - Updates history, analytics, and logs

### 5) Analytics & Admin
- `render_analytics_sidebar()` shows latest query, match score, time, and interest score chart
- `render_admin_panel()` lets you edit the DataFrame and save back to `fast_food_products.csv`

## 🛡️ Safety & Formatting
- Inappropriate/off-topic filtering (`_is_inappropriate_or_irrelevant`)
- Prices formatted as `$X.XX` via `_format_price`
- Ingredients rendered human-friendly (semicolon → comma)
- Strict “menu-only” responses; if info is unknown, the bot says so

## 🧪 Testing (optional)
We include an advanced test harness to evaluate formatting and behaviors.

Run:
```powershell
python advanced_test_suite.py
```

It checks: formatting, price display consistency, context quality, allergen safety, conversational flow, stress tests, and more.

## � Troubleshooting
- “No response until next message”: This has been addressed. The assistant reply is rendered immediately inside the assistant `chat_message` block. If you customize the UI, keep the `st.markdown(response)` inside that block.
- “LLM not available”: Ensure `.env` is present and `GROQ_API_KEY` is valid.
- “Embedding model error”: First run may take longer to download `all-MiniLM-L6-v2`.

## 📣 Contributing
PRs are welcome. Please open an issue to discuss larger changes.

---

Made with ❤️ to help restaurants deliver delightful, safe menu guidance.