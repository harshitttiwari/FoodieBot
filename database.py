#   database.py
import streamlit as st
import pandas as pd
import chromadb
from sentence_transformers import SentenceTransformer

DATA_FILE_PATH = "fast_food_products.csv"

@st.cache_resource
def initialize_services():
    """Load CSV, initialize ChromaDB, and build embeddings."""
    try:
        df = pd.read_csv(DATA_FILE_PATH)
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
        df["price"] = pd.to_numeric(df["price"], errors="coerce")
        df.dropna(subset=["price", "name", "product_id", "ingredients"], inplace=True)
    except FileNotFoundError:
        st.error("CSV file not found. Please place 'fast_food_products.csv' in the same folder as app.py.")
        return None, None, None
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None
    
    try:
        client = chromadb.Client()
        try:
            client.delete_collection("food_items") 
        except Exception:
            pass
        collection = client.create_collection("food_items")
    except Exception as e:
        st.error(f"Failed to initialize ChromaDB: {e}")
        return None, None, None
    try:
        embedder = SentenceTransformer("all-MiniLM-L6-v2")
    except Exception as e:
        st.error(f"Failed to load embedding model: {e}")
        return None, None, None
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
        embeddings = embedder.encode(documents).tolist()
        collection.add(documents=documents, embeddings=embeddings, metadatas=metadatas, ids=ids)
    except Exception as e:
        st.error(f"Failed to build embeddings: {e}")
        return None, None, None

    return df, collection, embedder

