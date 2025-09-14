#  database.py
import streamlit as st
import pandas as pd
import chromadb
from sentence_transformers import SentenceTransformer

DATA_FILE_PATH = 'fast_food_products.csv'

@st.cache_resource
def initialize_services():
    """
    Loads data, initializes ChromaDB, and sets up the embedding model.
    This function is cached to run only once, ensuring optimal performance.
    """
    st.info("Step 1/4: Loading product data from CSV...")
    try:
        df = pd.read_csv(DATA_FILE_PATH)
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        # Drop any rows missing essential information for the bot to function.
        df.dropna(subset=['price', 'name', 'product_id', 'ingredients'], inplace=True)
        st.info("Step 1/4: Product data loaded successfully! ✅")
    except FileNotFoundError:
        st.error(f"FATAL ERROR: `fast_food_products.csv` not found. Please make sure it's in the same folder as `app.py`.")
        return None, None, None
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None

    st.info("Step 2/4: Initializing vector database (ChromaDB)...")
    client = chromadb.Client()
    # Reset the collection for a clean start every time the app reloads.
    try:
        client.delete_collection("food_items")
    except Exception:
        pass # It's okay if the collection didn't exist.
    collection = client.create_collection("food_items")
    st.info("Step 2/4: Vector database initialized! ✅")

    st.info("Step 3/4: Loading sentence transformer model (this may take a moment on the first run)...")
    try:
        embedder = SentenceTransformer('all-MiniLM-L6-v2')
        st.info("Step 3/4: Sentence transformer model loaded! ✅")
    except Exception as e:
        st.error(f"Failed to load the embedding model. Please check your internet connection. Error: {e}")
        return None, None, None

    st.info("Step 4/4: Building rich database embeddings...")
    # **NEW**: We create more detailed documents for the search to make the bot smarter.
    # This includes ingredients, calories, and tags to prevent hallucination.
    df_records = df.to_dict('records')
    metadatas = [{str(k): str(v) for k, v in record.items()} for record in df_records]
    ids = [str(m['product_id']) for m in metadatas]
    documents = [
        f"Item Name: {row.get('name', '')}. Description: {row.get('description', '')}. Ingredients: {row.get('ingredients', '')}. Calories: {row.get('calories', 'N/A')}. Allergens: {row.get('allergens', 'None listed')}. Dietary Tags: {row.get('dietary_tags', '')}."
        for row in metadatas
    ]
    
    try:
        embeddings = embedder.encode(documents).tolist()
        collection.add(documents=documents, embeddings=embeddings, metadatas=metadatas, ids=ids)
        st.info("Step 4/4: Database embeddings built successfully! ✅")
    except Exception as e:
        st.error(f"Failed to build vector database: {e}")
        return None, None, None

    return df, collection, embedder



