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

# Function to render the map
def render_map(df):
    if df.empty:
        st.pydeck_chart( pdk.Deck(map_style='mapbox://styles/mapbox/outdoors-v11'))
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

    # Render the pydeck map
    r = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        map_style= 'mapbox://styles/mapbox/outdoors-v11'                                         
    )

    # Display the map in Streamlit
    st.pydeck_chart(r)

# Date input for start date
start_date = st.date_input('Start date', value=default_start_date)

# Date input for end date
end_date = st.date_input('End date', value=default_end_date, min_value=start_date, max_value=start_date + timedelta(days=50))

# Check if the date range is more than 50 days and show an error if it is
# Date input for start date
start_date = st.date_input('Start date', value=default_start_date)

# Date input for end date
end_date = st.date_input('End date', value=default_end_date, min_value=start_date, max_value=start_date + timedelta(days=50))

if (end_date - start_date).days > 50:
    st.error('The date range must not exceed 50 days.')
else:
    # Fetch data and prepare the map
    data = get_data(start_date, end_date)
    earthquakes = extract_data(data)
    df = pd.DataFrame(earthquakes)
    render_map(df)                           # Render the map on first load

# Button to update the map based on new input
if st.button('Update Map'):
    if (end_date - start_date).days <= 50 and start_date!=end_date:
        data = get_data(start_date, end_date)
        earthquakes = extract_data(data)
        df = pd.DataFrame(earthquakes)
        render_map(df)  # Update and render the map based on the new input
