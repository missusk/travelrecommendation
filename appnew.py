import streamlit as st
import pandas as pd
import nltk
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')
import numpy as np
from preprocessing_new import load_and_preprocess, tokenize_features
import pydeck as pdk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer


df = load_and_preprocess(r'C:\Users\memar\Downloads\intellitravel\hotels.csv')

def get_recommendations_by_name(hotel_name):
    idx = df[df['HotelName'] == hotel_name].index[0]
    return df.iloc[[idx]]

def get_recommendations_by_city(city, star_rating, features):
    lemm = WordNetLemmatizer()
    sw = stopwords.words('english')
    features_set = tokenize_features(features)
    reqbased = df[(df['cityName'] == city.lower()) & (df['HotelRating'] >= star_rating)]
    reqbased = reqbased.set_index(np.arange(reqbased.shape[0]))
    
    cos = []

    for i in range(reqbased.shape[0]):
        temp_tokens = word_tokenize(reqbased['HotelFacilities'][i])
        temp1_set = {w for w in temp_tokens if not w in sw}
        temp_set = set()
        for se in temp1_set:
            temp_set.add(lemm.lemmatize(se))
        rvector = temp_set.intersection(features_set)
        cos.append(len(rvector))
        
    reqbased['similarity'] = cos
    reqbased = reqbased.sort_values(by='similarity', ascending=False)
    reqbased.drop_duplicates(subset='HotelCode', keep='first', inplace=True)
    return reqbased[['cityName', 'HotelName', 'HotelRating', 'Address', 'HotelFacilities', 'Description', 'similarity']].head(10)

# Streamlit user interface
st.title('IntelliTravel - Hotel and Attraction Recommender System')
option = st.selectbox('Search by:', ['Hotel Name', 'City and Star Rating'])

recommendations = pd.DataFrame()

if option == 'Hotel Name':
    with st.form(key='hotel_name_form'):
        hotel_name = st.text_input('Enter the name of the hotel:')
        submit_button = st.form_submit_button(label='Find Similar Hotels')
        if submit_button:
            recommendations = get_recommendations_by_name(hotel_name)
            st.write(recommendations)
else:
    with st.form(key='city_star_form'):
        city = st.text_input('Enter city name:')
        star_rating = st.slider('Select minimum star rating:', 1, 5, 3)
        features = st.text_input('Enter desired features (comma separated):')
        submit_button = st.form_submit_button(label='Find Hotels')
        if submit_button:
            recommendations = get_recommendations_by_city(city, star_rating, features)
            st.write(recommendations)

# Displaying map of recommended hotels if any are found
if not recommendations.empty:
    map_data = recommendations[['Latitude', 'Longitude']]
    st.pydeck_chart(pdk.Deck(
         map_style='mapbox://styles/mapbox/light-v9',
         initial_view_state=pdk.ViewState(
             latitude=map_data['Latitude'].mean(),
             longitude=map_data['Longitude'].mean(),
             zoom=11,
             pitch=50,
         ),
         layers=[
             pdk.Layer(
                'ScatterplotLayer',
                data=map_data,
                get_position='[Longitude, Latitude]',
                get_color='[200, 30, 0, 160]',
                get_radius=200,
             ),
         ],
    ))
