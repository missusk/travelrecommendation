import streamlit as st
import pandas as pd
from models import get_similar_hotels, search_hotels, get_attractions

# Set the page configuration
st.set_page_config(page_title="IntelliTravel - Hotel Recommendation System", layout="wide", initial_sidebar_state="expanded")


st.markdown(
    """
    <style>
    .main {
        background-color: #341d4e;
    }
    .stButton>button {
        background-color: white;
        color: black;
        border-radius: 10px;
        border: 2px solid #007BFF;
    }
    .stButton>button:hover {
        background-color: #007BFF;
        color: white;
    }
    .card {
        background-color: #5d2d54;
        padding: 20px;
        margin: 10px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
    }
    .card-title {
        font-size: 24px;
        font-weight: bold;
        color: white;
    }
    .card-content {
        font-size: 18px;
        color: white;
    }
    .card a {
        color: white;
        text-decoration: none;
        font-weight: bold;
        background-color: #007BFF;
        padding: 10px;
        border-radius: 5px;
        display: inline-block;
        margin-top: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar 
st.sidebar.title("IntelliTravel")
st.sidebar.markdown("Navigate through the features:")
options = ["Home", "Find Similar Hotels", "Search Hotels by City, Star Rating, and Feature", "Check Out Attractions", "Contact Us"]
choice = st.sidebar.radio("", options)

# Home Page
if choice == "Home":
    st.title("Welcome to IntelliTravel")
    st.markdown(
        """
        ## Discover Your Perfect Hotel
        At IntelliTravel, we help you find the best hotels that match your preferences. Whether you're looking for a hotel similar to one you've stayed at before or searching for a new experience in a different city, we've got you covered.
        
        ### Our Features:
        - **Find Similar Hotels**: Discover hotels similar to the ones you love.
        - **Search Hotels by City, Star Rating, and Feature**: Tailor your search to find the perfect stay.
        - **Check Out Attractions**: Explore nearby attractions based on your hotel location.
        
        Start your journey with IntelliTravel and experience the best in hotel recommendations!
        """
    )

# Find Similar Hotels
elif choice == "Find Similar Hotels":
    st.title("Find Similar Hotels")
    st.markdown(
        "Liked a hotel you stayed in? Find out similar hotels in your destination city. Our recommendation engine will suggest you the best hotel for your best experience."
    )
    hotel_name = st.text_input("Enter the name of the hotel")
    target_city = st.text_input("Enter the city for finding similar hotels")
    if st.button("Find Similar Hotels"):
        similar_hotels = get_similar_hotels(hotel_name, target_city)
        if not similar_hotels.empty:
            for i, row in similar_hotels.iterrows():
                facilities = row['combined_facilities'].split('|')
                facilities_summary = ', '.join(facilities[:10]) + ('...' if len(facilities) > 10 else '')
                attractions_summary = ''
                if 'point_of_interest' in row and isinstance(row['point_of_interest'], str):
                    attractions = row['point_of_interest'].split('|')
                    attractions_summary = ', '.join(attractions[:5]) + ('...' if len(attractions) > 5 else '')
                
                address = row['address'] if pd.notna(row['address']) else 'Address not available'
                
                st.markdown(
                    f"""
                    <div class="card">
                        <div class="card-title">{row['property_name']}</div>
                        <div class="card-content">
                            <p><strong>Address:</strong> {address}</p>
                            <p><strong>Star Rating:</strong> {row['hotel_star_rating']}</p>
                            <p><strong>Review Rating:</strong> {row['site_review_rating']}</p>
                            <p><strong>Facilities:</strong> {facilities_summary}</p>
                            {'<p><strong>Nearby Attractions:</strong> ' + attractions_summary + '</p>' if attractions_summary else ""}
                            <a href="https://www.google.com/search?q={row['property_name']}+{target_city}" target="_blank">Book</a>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        else:
            st.write(f"No similar hotels found for {hotel_name} in {target_city}.")

# Search Hotels by City, Star Rating, and Feature
elif choice == "Search Hotels by City, Star Rating, and Feature":
    st.title("Search Hotels by City, Star Rating, and Feature")
    st.markdown(
        "Looking for the perfect hotel? Search by city, minimum star rating, and desired features to find the best options for your stay."
    )
    city = st.text_input("Enter city")
    star_rating = st.slider("Select minimum star rating",     1, 5, 3)
    feature = st.text_input("Enter feature (optional, comma-separated)")

    if st.button("Search Hotels"):
        results = search_hotels(city, star_rating, feature)
        if not results.empty:
            for i, row in results.iterrows():
                facilities = row['combined_facilities'].split('|')
                facilities_summary = ', '.join(facilities[:10]) + ('...' if len(facilities) > 10 else '')
                attractions_summary = ''
                if 'point_of_interest' in row and isinstance(row['point_of_interest'], str):
                    attractions = row['point_of_interest'].split('|')
                    attractions_summary = ', '.join(attractions[:5]) + ('...' if len(attractions) > 5 else '')
                
                address = row['address'] if pd.notna(row['address']) else 'Address not available'
                
                st.markdown(
                    f"""
                    <div class="card">
                        <div class="card-title">{row['property_name']}</div>
                        <div class="card-content">
                            <p><strong>Address:</strong> {address}</p>
                            <p><strong>Star Rating:</strong> {row['hotel_star_rating']}</p>
                            <p><strong>Review Rating:</strong> {row['site_review_rating']}</p>
                            <p><strong>Facilities:</strong> {facilities_summary}</p>
                            {'<p><strong>Nearby Attractions:</strong> ' + attractions_summary + '</p>' if attractions_summary else ''}
                            <a href="https://www.google.com/search?q={row['property_name']} {city}" target="_blank">Book</a>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.write(f"No hotels found in {city} with a minimum star rating of {star_rating} and features '{feature}'.")

# Check Out Attractions
elif choice == "Check Out Attractions":
    st.title("Check Out Attractions")
    st.markdown("Enter your hotel name and city to find nearby attractions. Discover what you can explore near your stay.")
    hotel_name = st.text_input("Enter your hotel name")
    city = st.text_input("Enter your city name")
    if st.button("Find Nearby Attractions"):
        attractions = get_attractions(hotel_name, city)
        if attractions:
            st.markdown("### Nearby Attractions:")
            for attraction in attractions:
                st.markdown(f"- {attraction}")
        else:
            st.write(f"No attractions found for {hotel_name} in {city}.")

# Contact Us
elif choice == "Contact Us":
    st.title("Contact Us")
    st.markdown(
        """
        If you have any questions or need assistance, feel free to reach out to us:
        - **Email**: [tech.maria.khan@gmail.com](mailto:tech.maria.khan@gmail.com)
        """
    )
