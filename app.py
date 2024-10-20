import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium
from fastkml import KML, Folder, Placemark  # Import the necessary KML classes
from shapely.geometry import Polygon, Point, LineString
import requests

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
            if isinstance(feature, Folder):
                for subfeature in feature.features():
                    if isinstance(subfeature, Placemark):
                        geometries.append(subfeature.geometry)
            elif isinstance(feature, Placemark):
                geometries.append(feature.geometry)

        # Debugging output to see what geometries were parsed
        st.write(f"Parsed Geometries: {geometries}")

        return geometries
    except Exception as e:
        st.error(f"An error occurred while parsing the KML file: {str(e)}")
        return []

def display_detailed_map():
    st.write("### Detailed Map with All KML Data:")

    # Read the CSV data
    df = pd.read_csv(CSV_URL)

    # Get the KML URL from the CSV file (assuming it's the last row in your dataset)
    kml_url = df.iloc[-1]["KML"]
    
    if not kml_url:
        st.error("No KML URL found in the CSV file.")
        return

    # Create a Folium map centered on the first project
    m = folium.Map(location=[df['Latitude'].mean(), df['Longitude'].mean()], zoom_start=12)

    # Add project locations to the map
    for i, row in df.iterrows():
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=f"{row['description']}<br><a href='{row['KML']}' target='_blank'>View KML File</a>",
        ).add_to(m)

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
st.title("Scan Your Releafs' Token")

# Display detailed map with all geometries
display_detailed_map()
