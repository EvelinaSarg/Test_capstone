import streamlit as st
import requests
import pandas as pd
import pydeck as pdk
from datetime import datetime, timedelta

# Streamlit app layout
st.title('Global Earthquake Activity Map')

# Set default dates for start and end date inputs
default_start_date = datetime.now() - timedelta(days=1)
default_end_date = datetime.now()

# Date input for start date
start_date = st.date_input('Start date', value=default_start_date, max_value=default_end_date - timedelta(days=1))

# Date input for end date
end_date = st.date_input('End date', value=default_end_date, min_value=start_date, max_value=start_date + timedelta(days=50))

# Check if the date range is more than 50 days and show an error if it is
if (end_date - start_date).days > 50:
    st.error('The date range must not exceed 50 days.')

# Function to make API call and get data
def get_data(start_date, end_date):
    url = f"https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime={start_date}&endtime={end_date}"
    response = requests.get(url)
    return response.json()

# Function to extract places, coordinates, and magnitudes
def extract_data(data):
    earthquakes = []
    for feature in data['features']:
        properties = feature['properties']
        geometry = feature['geometry']
        earthquakes.append({
            'place': properties['place'],
            'magnitude': properties['mag'],
            'longitude': geometry['coordinates'][0],
            'latitude': geometry['coordinates'][1]
        })
    return earthquakes

# Display data on a map
if st.button('Show Map') and (end_date - start_date).days <= 50:
    data = get_data(start_date, end_date)
    earthquakes = extract_data(data)
    df = pd.DataFrame(earthquakes)

    # Define the pydeck layer
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position='[longitude, latitude]',
        get_radius='magnitude * 50000',  # Adjust the size of the scatterplot
        get_color='[180, 0, 200, 140]',  # RGBA color for the scatterplot
        pickable=True,
        auto_highlight=True,
    )

    # Tooltip configuration for showing the magnitude on hover
    tooltip = {
        "html": "<b>Place:</b> {place} <br/> <b>Magnitude:</b> {magnitude}",
        "style": {
            "backgroundColor": "steelblue",
            "color": "white"
        }
    }

    # Define the initial view state for pydeck
    view_state = pdk.ViewState(
        latitude=df['latitude'].mean(),
        longitude=df['longitude'].mean(),
        zoom=1,
        pitch=0,
    )

    # Render the pydeck map with tooltip
    r = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        map_style='mapbox://styles/mapbox/light-v9',
        tooltip=tooltip
    )

    # Display the map in Streamlit
    st.pydeck_chart(r)
