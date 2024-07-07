import pandas as pd
import numpy as np
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import streamlit as st
import diskcache as dc

cache = dc.Cache("cache_dir")

def load_data(filepath):
    return pd.read_csv(filepath, encoding = 'latin-1')


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
    df['cityName'] = df['cityName'].str.lower()
    df['HotelFacilities'] = df['HotelFacilities'].str.lower()
    rating_mapping = {
        'OneStar': 1,
        'TwoStar': 2,
        'ThreeStar': 3,
        'FourStar': 4,
        'FiveStar': 5
    }
    df['HotelRating'] = df['HotelRating'].map(rating_mapping)
    
    return df

@st.cache_data
def tokenize_features(features):
    features = features.lower()
    features_tokens = word_tokenize(features)
    sw = stopwords.words('english')
    lemm = WordNetLemmatizer()
    f1_set = {w for w in features_tokens if not w in sw}
    f_set = set()
    for se in f1_set:
        f_set.add(lemm.lemmatize(se))
    return f_set

@st.cache_data
def load_and_preprocess(filepath):
    if 'df' not in cache:
        df = load_data(filepath)
        df = preprocess_data(df)
        cache.set('df', df)
    else:
        df = cache.get('df')
    return df