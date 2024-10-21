import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
import xml.etree.ElementTree as ET

# Define the URL to your CSV file hosted on GitHub
CSV_URL = "https://raw.githubusercontent.com/hawkarabdulhaq/impactdashboard/main/impactdata.csv"

def parse_kml_with_etree(kml_url):
    """Download and parse the KML file using xml.etree.ElementTree, extracting placemarks."""
    if "drive.google.com" in kml_url:
        # Convert the Google Drive link to a direct download link
        file_id = kml_url.split("/d/")[1].split("/")[0]
        kml_url = f"https://drive.google.com/uc?export=download&id={file_id}"

    # Download the KML file
    response = requests.get(kml_url)
    if response.status_code != 200:
        st.error("Failed to download the KML file.")
        return []

    # Parse KML data using ElementTree
    try:
        tree = ET.ElementTree(ET.fromstring(response.content))
        root = tree.getroot()

        # Namespace handling
        ns = {'kml': 'http://www.opengis.net/kml/2.2'}

        # Extract placemarks
        placemarks = []
        for placemark in root.findall('.//kml:Placemark', ns):
            name = placemark.find('kml:name', ns)
            description = placemark.find('kml:description', ns)
            point = placemark.find('.//kml:Point/kml:coordinates', ns)

            if point is not None:
                coords = point.text.strip().split(',')
                lon, lat = float(coords[0]), float(coords[1])
                placemarks.append({
                    'name': name.text if name is not None else 'Unnamed Placemark',
                    'description': description.text if description is not None else 'No Description',
                    'lat': lat,
                    'lon': lon
                })
        return placemarks

    except ET.ParseError as e:
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

    st.write(f"Using KML URL: {kml_url}")  # Debug: Output the KML URL

    # Create a Folium map, centering on the first project location
    m = folium.Map(location=[df['Latitude'].mean(), df['Longitude'].mean()], zoom_start=12)

    # Parse and display the KML data
    placemarks = parse_kml_with_etree(kml_url)

    if placemarks:
        st.write(f"Extracted Placemarks Count: {len(placemarks)}")  # Debug: Output number of placemarks extracted

        for placemark in placemarks:
            st.write(f"Placemark: {placemark['name']}, Coordinates: ({placemark['lat']}, {placemark['lon']})")  # Debug: Output placemark info

            # Add marker to the map
            folium.Marker(
                location=[placemark['lat'], placemark['lon']],
                popup=f"<b>{placemark['name']}</b><br>{placemark['description']}"
            ).add_to(m)
    else:
        st.error("No valid placemarks found in the KML file.")

    # Display the map in Streamlit
    st_folium(m, width=700, height=500)

# Streamlit Page Layout
st.title("KML File Viewer")

# Display KML data from the URL in the CSV file
display_kml_map()
