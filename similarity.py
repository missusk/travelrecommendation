from sklearn.metrics.pairwise import cosine_similarity 
import streamlit as st

@st.cache_resource
def calculate_cosine_similarity(_tfidf_matrix):
    return cosine_similarity(_tfidf_matrix)