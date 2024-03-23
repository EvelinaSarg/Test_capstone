
import streamlit as st
import requests
import pandas as pd
import psycopg2
import matplotlib.pyplot as plt
from sqlalchemy import create_engine

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
# Set up your database connection here
db_user = 'de_evsa'
db_password = 'guisities'
db_host = 'data-sandbox.c1tykfvfhpit.eu-west-2.rds.amazonaws.com'
db_port = 5432
db_name = 'pagila'
db_table = 'evsa_earthquakes'

# Streamlit app title
st.title('Earthquake Data Visualization')

# Function to load data from the database
def load_data():
    engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')
    query = f'SELECT * FROM {db_table}'  # Adjust the query to match your table structure
    data = pd.read_sql(query, engine)
    return data

# Button to refresh data
if st.button('Refresh Data'):
    st.legacy_caching.clear_cache()  # Clear the Streamlit cache
    data = load_data()  # Reload the data
    st.experimental_rerun()  # Rerun the Streamlit app to update the plot

# Load the data
data = load_data()

# Plot the data if it's loaded
if not data.empty:
    # Assuming 'date' and 'earthquakes' are columns in your table
    fig, ax = plt.subplots()
    ax.plot(data['date'], data['earthquakes'], marker='o')
    ax.set_title('Number of Earthquakes Over Time')
    ax.set_xlabel('Date')
    ax.set_ylabel('Number of Earthquakes')
    ax.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Display the plot in Streamlit
    st.pyplot(fig)
else:
    st.write('No data available to display.')

