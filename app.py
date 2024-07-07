import streamlit as st
import pandas as pd
from data_processing import load_data, preprocess_data, create_tfidf_matrix
from similarity import calculate_cosine_similarity
import pydeck as pdk


df = load_data(r'C:\Users\memar\Downloads\intellitravel\hotels.csv')
df = preprocess_data(df)


tfidf_matrix = create_tfidf_matrix(df)


cosine_sim = calculate_cosine_similarity(tfidf_matrix)

def get_recommendations_by_name(hotel_name):
    idx = df[df['HotelName'] == hotel_name].index[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:11]  
    hotel_indices = [i[0] for i in sim_scores]
    return df.iloc[hotel_indices]

def get_recommendations_by_city(city, star_rating):
    matched_hotels = df[(df['cityName'].str.lower() == city.lower()) & (df['HotelRating'] >= star_rating)]
    return matched_hotels

# user interface
st.title('Hotel and Attraction Recommender System')
option = st.selectbox('Search by:', ['Hotel Name', 'City and Star Rating'])

recommendations = pd.DataFrame()

if option == 'Hotel Name':
    hotel_name = st.text_input('Enter the name of the hotel:')
    if st.button('Find Similar Hotels'):
        recommendations = get_recommendations_by_name(hotel_name)
        st.write(recommendations)
else:
    city = st.text_input('Enter city name:')
    star_rating = st.slider('Select minimum star rating:', 1, 5, 3)
    if st.button('Find Hotels'):
        recommendations = get_recommendations_by_city(city, star_rating)
        st.write(recommendations)


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
