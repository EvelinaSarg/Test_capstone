
import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from datetime import datetime, timedelta #added
import pydeck as pdk                                            

st.title('Global Earthquake Activity Map')

# Function to make API call and get data
def get_data(start_date, end_date):
    url = f"https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime={start_date}&endtime={end_date}"
    response = requests.get(url)
    return response.json()

# Function to extract places, coordinates, and magnitudes
def extract_data(data):
    earthquakes = []
    for feature in data['features']:
        place = feature['properties']['place']
        longitude, latitude = feature['geometry']['coordinates'][0:2]
        magnitude = feature['properties']['mag']
        earthquakes.append({
            'place': place,
            'magnitude': magnitude,
            'longitude': longitude,
            'latitude': latitude
        })
    return earthquakes

# Function to render the map
def render_map(df):
    if df.empty:
        st.pydeck_chart( pdk.Deck(map_style='mapbox://styles/mapbox/outdoors-v11')) #added
        st.warning('No earthquake data available for the selected date range.')
        return
    # Define the pydeck layer
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position='[longitude, latitude]',
        get_radius='magnitude * 50000',  # Adjust the size based on magnitude
        get_color='[180, 0, 200, 140]',  # RGBA color
        pickable=True,
        auto_highlight=True,
    )
    # Define the initial view state for pydeck
    view_state = pdk.ViewState(
        latitude=df['latitude'].mean(),
        longitude=df['longitude'].mean(),
        zoom=1,
        pitch=0,
    )
    r = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        map_style= 'mapbox://styles/mapbox/outdoors-v11',
        tooltip= {
        "html": "<b>Place:</b> {place} <br/> <b>Magnitude:</b> {magnitude}",
        "style": {
            "backgroundColor": "steelblue",
            "color": "white"
        } }                                      
    )

    # Display the map in Streamlit
    st.pydeck_chart(r)
    
    
start_date = st.date_input('Start date', value=datetime.now() - timedelta(days=1))
end_date = st.date_input('End date', value=datetime.now())

if (end_date - start_date).days > 50:
    st.error('The date range must not exceed 50 days.')
elif end_date<start_date:
    st.warning("Start can't be later than the end date.") #added to remove
else:
    # Fetch data and prepare the map
    data = get_data(start_date, end_date)
    earthquakes = extract_data(data)
    df = pd.DataFrame(earthquakes)
    render_map(df)                           # Render the map on first load


