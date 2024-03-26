import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine

# Streamlit app layout
st.title('Earthquake Data Viewer')

# Date input
start_date = st.date_input('Start date', min_value=datetime(2020, 1, 1), max_value=datetime(current_year, 12, 31))
end_date = st.date_input('End date', min_value=datetime(2020, 1, 1), max_value=datetime(current_year, 12, 31))
#-----------------------------------------------------
#added line
if (end_date - start_date).days > 50:
    st.error('The date range must not exceed 50 days.')
#------------------------------------------------
# Function to make API call
def get_data(start_date, end_date):
    url = f"https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime={start_date}&endtime={end_date}"
    response = requests.get(url)
    return response.json()

# Function to extract places and coordinates
def extract_places(data):
    places = []
    for item in data['features']:
        place = item['properties']['place']
        longitude, latitude = item['geometry']['coordinates'][0:2]
        places.append({'place': place, 'latitude': latitude, 'longitude': longitude})
    return places

# Display data on a map
if st.button('Show Data'):
    data = get_data(start_date, end_date)
    places = extract_places(data)

    # Convert to DataFrame for Streamlit map
    df = pd.DataFrame(places)
    st.map(df)


