import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium
from fastkml import KML
import requests
from shapely.geometry import Point, LineString, Polygon

# Define the URL to your CSV file hosted on GitHub
CSV_URL = "https://raw.githubusercontent.com/hawkarabdulhaq/impactdashboard/main/impactdata.csv"

def parse_kml(kml_url):
    """Parses the KML file and extracts all geometries (polygons, lines, points)."""
    if "drive.google.com" in kml_url:
        # Convert the Google Drive link to a direct download link
        file_id = kml_url.split("/d/")[1].split("/")[0]
        kml_url = f"https://drive.google.com/uc?export=download&id={file_id}"

    # Download the KML file
    response = requests.get(kml_url)

    # Check if the response is valid
    if response.status_code != 200:
        st.error("Failed to download KML file.")
        return []

    kml_data = response.text

    try:
        k = KML()
        k.from_string(kml_data)

        geometries = []
        # Parse through KML features, handling Folders and Placemarks
        for feature in k.features():
            if hasattr(feature, 'features'):
                for subfeature in feature.features():
                    if hasattr(subfeature, 'geometry'):
                        geometries.append(subfeature.geometry)
            elif hasattr(feature, 'geometry'):
                geometries.append(feature.geometry)

        return geometries
    except Exception as e:
        st.error(f"An error occurred while parsing the KML file: {str(e)}")
        return []

def display_kml_map():
    st.write("### Map Displaying KML Data")

    # Read the CSV data
    df = pd.read_csv(CSV_URL)

    # Get the KML URL from the last row in the CSV file
    kml_url = df.iloc[-1]["KML"]
    
    if not kml_url:
        st.error("No KML URL found in the CSV file.")
        return

    # Create a Folium map centered on the first project
    m = folium.Map(location=[df['Latitude'].mean(), df['Longitude'].mean()], zoom_start=12)

    # Parse KML and add geometries to the map
    geometries = parse_kml(kml_url)

    for geometry in geometries:
        # Add Points
        if isinstance(geometry, Point):
            folium.Marker(location=[geometry.y, geometry.x], popup="Point").add_to(m)
        # Add LineStrings
        elif isinstance(geometry, LineString):
            coords = [(point[1], point[0]) for point in geometry.coords]
            if coords:
                folium.PolyLine(locations=coords, color='green').add_to(m)
        # Add Polygons
        elif isinstance(geometry, Polygon):
            coords = [(pt[1], pt[0]) for pt in geometry.exterior.coords]  # Lat, Lon format
            if coords:
                folium.Polygon(locations=coords, color='blue', fill=True, fill_opacity=0.4).add_to(m)

    # Display the Folium map in Streamlit
    st_folium(m, width=700, height=500)

# Streamlit Page Layout
st.title("Display KML Data from Google Drive")

# Call the function to display the map
display_kml_map()
