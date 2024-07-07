import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load the cleaned dataset
df = pd.read_csv('cleaned_goibibo_com-travel_sample.csv')

# Fill missing values in the point_of_interest column
df['point_of_interest'].fillna('No attractions|', inplace=True)

# Combine text features for similarity search
df['combined_text'] = df['hotel_description'].fillna('') + ' ' + df['combined_facilities'].fillna('')

def get_similar_hotels(hotel_name, target_city):
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df['combined_text'])
    
    # Find hotels containing the hotel_name substring, case-insensitive
    matching_hotels = df[df['property_name'].str.contains(hotel_name, case=False)]
    if matching_hotels.empty:
        return pd.DataFrame(columns=['property_name', 'hotel_star_rating', 'site_review_rating', 'combined_facilities'])
    
    hotel_idx = matching_hotels.index[0]
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    
    sim_scores = list(enumerate(cosine_sim[hotel_idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:]  # remove the first element (itself)
    
    similar_hotels_indices = [i[0] for i in sim_scores]
    similar_hotels_df = df.iloc[similar_hotels_indices]
    
    # Filter by target city
    similar_hotels_df = similar_hotels_df[similar_hotels_df['city'].str.lower() == target_city.lower()]
    
    if similar_hotels_df.empty:
        return pd.DataFrame(columns=['property_name', 'hotel_star_rating', 'site_review_rating', 'combined_facilities'])
    
    # Get star rating of the original hotel
    original_hotel_star_rating = df.loc[hotel_idx, 'hotel_star_rating']
    
    # Filter similar hotels based on star rating (>= original hotel star rating)
    similar_hotels_df = similar_hotels_df[similar_hotels_df['hotel_star_rating'] >= original_hotel_star_rating]
    
    # Sort similar hotels by star rating and site review rating
    similar_hotels_df = similar_hotels_df.sort_values(by=['hotel_star_rating', 'site_review_rating'], ascending=[False, False])
    
    # Get top N similar hotels in the target city
    top_similar_hotels = similar_hotels_df.head()
    return top_similar_hotels[['property_name', 'hotel_star_rating', 'site_review_rating', 'combined_facilities', 'city', 'pageurl', 'point_of_interest', 'address']]

def search_hotels(city, star_rating, feature):
    filtered_df = df[(df['city'].str.lower() == city.lower()) & (df['hotel_star_rating'] >= star_rating)]
    if feature:
        features = feature.lower().split(',')
        for feat in features:
            filtered_df = filtered_df[filtered_df['combined_facilities'].str.contains(feat.strip(), case=False, na=False)]
    
    if filtered_df.empty:
        return pd.DataFrame(columns=['property_name', 'hotel_star_rating', 'site_review_rating', 'combined_facilities', 'point_of_interest'])
    
    filtered_df = filtered_df.sort_values(by='site_review_rating', ascending=False)
    top_hotels = filtered_df.head()[['property_name', 'hotel_star_rating', 'site_review_rating', 'combined_facilities', 'point_of_interest', 'city', 'address']]
    return top_hotels

def get_attractions(hotel_name, city):
    city_hotels = df[df['city'].str.lower() == city.lower()]
    hotel = city_hotels[city_hotels['property_name'].str.contains(hotel_name, case=False, na=False)]
    
    if not hotel.empty:
        attractions = hotel.iloc[0]['point_of_interest']
        if pd.notna(attractions):
            return attractions.split('|') 
    return []
