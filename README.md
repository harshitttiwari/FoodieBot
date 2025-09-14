# 🤖 FoodieBot - AI Restaurant Assistant

A smart, conversational restaurant assistant built with Streamlit and powered by Groq's LLM. FoodieBot helps customers explore your menu, handles allergen restrictions safely, and provides personalized food recommendations.

## ✨ Features

- **🍔 Smart Menu Navigation** - Browse 100+ food items across categories
- **🚨 Allergen Safety** - Strict filtering to prevent dangerous recommendations
- **🌶️ Spice Level Intelligence** - Auto-suggests cooling drinks for spicy orders
- **💬 Natural Conversation** - Handles casual chat and food questions naturally
- **📊 Live Analytics** - Real-time query monitoring and interest tracking
- **⚡ Fast Search** - Vector-based menu search with ChromaDB
- **🛡️ Content Filtering** - Blocks inappropriate content and gibberish

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Groq API Key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/FoodieBot.git
   cd FoodieBot
   ```

2. **Install dependencies**
   ```bash
   pip install streamlit langchain-groq pandas chromadb sentence-transformers python-dotenv
   ```

3. **Set up environment**
   ```bash
   # Create .env file
   echo "GROQ_API_KEY=your-groq-api-key-here" > .env
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Open your browser** to `http://localhost:8501`

## 📁 Project Structure

```
FoodieBot/
├── app.py                 # Main Streamlit application
├── bot_logic.py          # AI response logic and filtering
├── ui_components.py      # UI rendering and enhanced context
├── database.py           # Data loading and vector database setup
├── fast_food_products.csv # Menu database (100 items)
├── test_improvements.py  # Comprehensive test suite
├── .env                  # Environment variables (create this)
└── README.md            # This file
```

## 🎯 How It Works

1. **Menu Loading** - Loads 100+ food items from CSV into ChromaDB vector database
2. **Smart Search** - Uses sentence transformers to find relevant menu items
3. **Context Building** - Filters by allergens and categorizes food types
4. **AI Response** - Groq LLM generates natural, helpful responses
5. **Safety Checks** - Multiple layers of filtering for safety and appropriateness

## 🛡️ Safety Features

- **Allergen Protection** - Never recommends items with trace allergens
- **Content Filtering** - Blocks inappropriate content and gibberish
- **Response Cleaning** - Removes AI internal monologue for natural chat
- **Menu-Only Focus** - Redirects off-topic questions back to food

## 📊 Testing

Run the comprehensive test suite:
```bash
python test_improvements.py
```

Tests cover:
- Gibberish filtering
- Allergen safety
- Response formatting
- Context building
- Conversational handling

## 🔧 Configuration

### Environment Variables (.env)
```
GROQ_API_KEY=your-groq-api-key-here
```

### Menu Customization
Edit `fast_food_products.csv` to customize your restaurant's menu. Required columns:
- `name` - Item name
- `price` - Price (numeric)
- `ingredients` - Semicolon-separated ingredients
- `allergens` - Allergen information
- `category` - Food category
- `spice_level` - Heat level (0-10)

## 🎨 UI Components

- **Chat Interface** - Real-time conversation with the bot
- **Analytics Sidebar** - Live query stats and interest tracking
- **Admin Panel** - Edit menu items directly in the interface

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Groq** - Fast LLM inference
- **Streamlit** - Beautiful web interface
- **ChromaDB** - Vector database for semantic search
- **LangChain** - LLM integration framework

## 📧 Support

If you encounter any issues or have questions:
1. Check the test suite: `python test_improvements.py`
2. Review the logs in the Streamlit interface
3. Open an issue on GitHub

---

**Made with ❤️ for restaurant owners who want to provide better customer service through AI**