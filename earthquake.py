
import streamlit as st
import requests
import pandas as pd
import pydeck as pdk
import numpy as np
# Streamlit app layout
st.title('Earthquake Data Viewer')

# Date input
start_date = st.date_input('Start date')
end_date = st.date_input('End date')

# Function to make API call
def get_data(start_date, end_date):
    url = f"https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime={start_date}&endtime={end_date}"
    response = requests.get(url)
    return response.json()

# Function to extract places, coordinates, and magnitudes
def extract_places_and_magnitudes(data):
    earthquakes = []
    for item in data['features']:
        place = item['properties']['place']
        magnitude = item['properties']['mag']
        longitude, latitude = item['geometry']['coordinates'][0:2]
        earthquakes.append({'place': place, 'latitude': latitude, 'longitude': longitude, 'magnitude': magnitude})
    return earthquakes

# Display data on a map
if st.button('Show Data'):
    data = get_data(start_date, end_date)
    earthquakes = extract_places_and_magnitudes(data)
    df = pd.DataFrame(earthquakes)

    # Set up a pydeck map
    view_state = pdk.ViewState(latitude=df['latitude'].mean(), longitude=df['longitude'].mean(), zoom=1, bearing=0, pitch=0)
    layer = pdk.Layer(
        'ScatterplotLayer',
        data=df,
        get_position='[longitude, latitude]',
        get_color='[200, 30, 0, 160]',
        get_radius='[magnitude * 10000]',
    )

    st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state,  map_style=None))


