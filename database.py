# database.py
import os
import streamlit as st
import pandas as pd
import chromadb
from sentence_transformers import SentenceTransformer

DATA_FILE_PATH = "fast_food_products.csv"

@st.cache_resource
def initialize_services():
    """Load CSV, initialize ChromaDB, and build embeddings."""
    # Step 1: Load CSV
    try:
        df = pd.read_csv(DATA_FILE_PATH)
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
        df["price"] = pd.to_numeric(df["price"], errors="coerce")
        df.dropna(subset=["price", "name", "product_id", "ingredients"], inplace=True)
    except FileNotFoundError:
        st.error("❌ CSV file not found. Place 'fast_food_products.csv' in the root folder.")
        return None, None, None
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        return None, None, None

    # Step 2: Setup ChromaDB
    try:
        client = chromadb.Client()
        try:
            client.delete_collection("food_items")
        except Exception:
            pass
        collection = client.create_collection("food_items")
    except Exception as e:
        st.error(f"❌ Failed to initialize ChromaDB: {e}")
        return None, None, None

    # Step 3: Load Sentence Transformer safely (ensure writable cache)
    try:
        cache_dir = os.environ.get("HF_HOME", "/tmp/hf_cache")
        os.makedirs(cache_dir, exist_ok=True)
        # Many platforms set unwritable defaults like /app/model_cache.
        # Force all transformers caches to /tmp to avoid permission issues.
        os.environ.setdefault("TRANSFORMERS_CACHE", cache_dir)
        os.environ.setdefault("HF_HOME", cache_dir)
        embedder = SentenceTransformer("all-MiniLM-L6-v2", cache_folder=cache_dir)
    except Exception as e:
        st.error(f"❌ Failed to load embedding model: {e}")
        return None, None, None

    # Step 4: Build embeddings
    try:
        records = df.to_dict("records")
        metadatas = [{str(k): str(v) for k, v in rec.items()} for rec in records]
        ids = [str(m["product_id"]) for m in metadatas]

        documents = [
            f"Item Name: {r.get('name','')}. "
            f"Description: {r.get('description','')}. "
            f"Ingredients: {r.get('ingredients','')}. "
            f"Calories: {r.get('calories','N/A')}. "
            f"Allergens: {r.get('allergens','None listed')}. "
            f"Dietary Tags: {r.get('dietary_tags','')}."
            for r in metadatas
        ]
        embeddings = embedder.encode(documents, show_progress_bar=False).tolist()

        collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
    except Exception as e:
        st.error(f"❌ Failed to build embeddings: {e}")
        return None, None, None

    return df, collection, embedder
