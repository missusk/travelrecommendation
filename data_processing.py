import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import streamlit as st 

def load_data(filename):
    df = pd.read_csv(filename, encoding='latin-1')
    return df

@st.cache_data
def preprocess_data(df):
    df.columns = df.columns.str.strip()
    df.dropna(subset=['PinCode'], inplace=True)
    df.dropna(subset=['Description'], inplace=True)
    df.dropna(subset=['Address'], inplace=True)
    df.dropna(subset=['Map'], inplace=True)
    df.dropna(subset=['HotelFacilities'], inplace=True)
    df.dropna(subset=['Attractions'], inplace=True)
    df.drop(['FaxNumber', 'PhoneNumber', 'HotelWebsiteUrl'], axis = 1, inplace = True)
    if 'Map' in df.columns:
        coords = df['Map'].str.split('|', expand=True)
        df['Latitude'] = pd.to_numeric(coords[0].str.strip(), errors='coerce')
        df['Longitude'] = pd.to_numeric(coords[1].str.strip(), errors='coerce')

    df.dropna(subset=['Latitude', 'Longitude'], inplace=True)
    
    df['content'] = df['Description'] + ' ' + df['HotelFacilities'] + ' ' + df['Attractions']
    
    return df

@st.cache_data
def create_tfidf_matrix(df):
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df['content'])
    return tfidf_matrix