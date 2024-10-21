import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium
from fastkml import KML  # Import only the KML class
from shapely.geometry import Point, LineString, Polygon
import requests

# Define the URL to your CSV file hosted on GitHub
CSV_URL = "https://raw.githubusercontent.com/hawkarabdulhaq/impactdashboard/main/impactdata.csv"

def parse_kml(kml_url):
    """Download and parse the KML file, extracting all geometries (polygons, lines, points)."""
    if "drive.google.com" in kml_url:
        # Convert the Google Drive link to a direct download link
        file_id = kml_url.split("/d/")[1].split("/")[0]
        kml_url = f"https://drive.google.com/uc?export=download&id={file_id}"

    # Download the KML file
    response = requests.get(kml_url)

    if response.status_code != 200:
        st.error("Failed to download the KML file.")
        return []

    kml_data = response.text

    try:
        kml_obj = KML()
        kml_obj.from_string(kml_data)

        geometries = []
        # Loop through the KML features and extract geometries
        for feature in kml_obj.features():
            for placemark in feature.features():
                geometries.append(placemark.geometry)

        return geometries
    except Exception as e:
        st.error(f"Error parsing KML file: {e}")
        return []

def display_kml_map():
    st.write("### KML Data Viewer")

    # Load the CSV file
    df = pd.read_csv(CSV_URL)

    # Extract the KML URL from the last row of the CSV file
    kml_url = df.iloc[-1]["KML"]
    
    if not kml_url:
        st.error("No KML URL found in the CSV file.")
        return

    # Create a Folium map, centering on the first project location
    m = folium.Map(location=[df['Latitude'].mean(), df['Longitude'].mean()], zoom_start=12)

    # Parse and display the KML data
    geometries = parse_kml(kml_url)
    
    if geometries:
        for geometry in geometries:
            # Handle Points
            if isinstance(geometry, Point):
                folium.Marker(location=[geometry.y, geometry.x], popup="Point").add_to(m)
            # Handle LineStrings
            elif isinstance(geometry, LineString):
                coords = [(point[1], point[0]) for point in geometry.coords]
                folium.PolyLine(locations=coords, color='green').add_to(m)
            # Handle Polygons
            elif isinstance(geometry, Polygon):
                coords = [(pt[1], pt[0]) for pt in geometry.exterior.coords]
                folium.Polygon(locations=coords, color='blue', fill=True, fill_opacity=0.4).add_to(m)

    else:
        st.error("No valid geometries found in the KML file.")

    # Display the map in Streamlit
    st_folium(m, width=700, height=500)

# Streamlit Page Layout
st.title("KML File Viewer")

# Display KML data from the URL in the CSV file
display_kml_map()
