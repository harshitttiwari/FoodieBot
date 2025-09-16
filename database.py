# database.py

import os
import streamlit as st
import pandas as pd
import chromadb
from sentence_transformers import SentenceTransformer
# --- FIX Step 1: Import ChromaDB's embedding function utility ---
from chromadb.utils import embedding_functions

# Create a reliable path to the CSV file
script_dir = os.path.dirname(__file__)
DATA_FILE_PATH = os.path.join(script_dir, "fast_food_products.csv")

@st.cache_resource
def initialize_services():
    """Load CSV, initialize ChromaDB, and build embeddings."""
    # Step 1: Load CSV (No changes here)
    try:
        df = pd.read_csv(DATA_FILE_PATH)
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
        df["price"] = pd.to_numeric(df["price"], errors="coerce")
        df.dropna(subset=["price", "name", "product_id", "ingredients"], inplace=True)
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        return None, None, None

    # --- FIX Step 2: Define your embedding function for ChromaDB ---
    # Use the writable cache folder you already configured.
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2",
        cache_folder="/tmp/model_cache"
    )

    # Step 2: Setup ChromaDB
    try:
        client = chromadb.Client()
        # --- FIX Step 3: Pass the embedding function when creating the collection ---
        collection = client.get_or_create_collection(
            name="food_items",
            embedding_function=sentence_transformer_ef # This is the crucial part
        )
    except Exception as e:
        st.error(f"❌ Failed to initialize ChromaDB: {e}")
        return None, None, None

    # Step 3 is now part of Step 2, so we can remove the old embedder loading.

    # Step 4: Build and add embeddings to the collection
    try:
        if collection.count() == 0:
            st.info("Building new vector embeddings for product data...")
            records = df.to_dict("records")
            ids = [str(rec["product_id"]) for rec in records]
            # ChromaDB will now automatically use the assigned function to create embeddings
            documents = [
                f"Item Name: {r.get('name','')}. "
                f"Description: {r.get('description','')}. "
                f"Ingredients: {r.get('ingredients','')}. "
                f"Calories: {r.get('calories','N/A')}. "
                f"Allergens: {r.get('allergens','None listed')}."
                for r in records
            ]
            collection.add(
                documents=documents,
                metadatas=records,
                ids=ids
            )
            st.info("Embeddings created successfully.")
        else:
            st.info("Using existing embeddings from vector DB.")
    except Exception as e:
        st.error(f"❌ Failed to build embeddings: {e}")
        return None, None, None

    # We return the embedding function itself now instead of the raw model
    return df, collection, sentence_transformer_ef