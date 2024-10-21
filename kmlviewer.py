import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium
from fastkml import KML, Document, Folder, Placemark  # Import necessary classes for KML parsing
import requests

# Define the URL to your CSV file hosted on GitHub
CSV_URL = "https://raw.githubusercontent.com/hawkarabdulhaq/impactdashboard/main/impactdata.csv"

def extract_features_from_kml(feature):
    """Recursively extract all features (placemarks, folders, etc.) from the KML."""
    all_features = []
    if isinstance(feature, Document) or isinstance(feature, Folder):
        # Loop through all features inside a Document or Folder
        for subfeature in feature.features():
            all_features.extend(extract_features_from_kml(subfeature))
    elif isinstance(feature, Placemark):
        # Capture placemark features
        all_features.append(feature)
    return all_features

def parse_kml(kml_url):
    """Download and parse the KML file, extracting all features (not just geometries)."""
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

        # Debug: Output first 500 characters of KML data for verification
        st.write(f"KML Data: {kml_data[:500]}...")

        # Extract and return all features from the KML, including from Document or Folder
        return extract_features_from_kml(kml_obj)

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

    st.write(f"Using KML URL: {kml_url}")  # Debug: Output the KML URL

    # Create a Folium map, centering on the first project location
    m = folium.Map(location=[df['Latitude'].mean(), df['Longitude'].mean()], zoom_start=12)

    # Parse and display the KML data
    features = parse_kml(kml_url)
    
    if features:
        st.write(f"Extracted Features Count: {len(features)}")  # Debug: Output number of features extracted

        for feature in features:
            if isinstance(feature, Placemark):
                name = feature.name if feature.name else "Unnamed Placemark"
                description = feature.description if feature.description else "No Description"
                geometry = feature.geometry
                
                st.write(f"Feature: {name}, Geometry: {geometry.geom_type if geometry else 'No Geometry'}")  # Debug: Output feature info

                if geometry:
                    # Handle Points
                    if geometry.geom_type == 'Point':
                        folium.Marker(
                            location=[geometry.y, geometry.x], 
                            popup=f"<b>{name}</b><br>{description}"
                        ).add_to(m)
                    # Handle LineStrings
                    elif geometry.geom_type == 'LineString':
                        coords = [(point[1], point[0]) for point in geometry.coords]
                        folium.PolyLine(locations=coords, color='green').add_to(m)
                    # Handle Polygons
                    elif geometry.geom_type == 'Polygon':
                        coords = [(pt[1], pt[0]) for pt in geometry.exterior.coords]
                        folium.Polygon(locations=coords, color='blue', fill=True, fill_opacity=0.4).add_to(m)
                else:
                    # No geometry, just display metadata as a marker at a default location
                    folium.Marker(
                        location=[df['Latitude'].mean(), df['Longitude'].mean()], 
                        popup=f"<b>{name}</b><br>{description}"
                    ).add_to(m)
    else:
        st.error("No valid features found in the KML file.")

    # Display the map in Streamlit
    st_folium(m, width=700, height=500)

# Streamlit Page Layout
st.title("KML File Viewer")

# Display KML data from the URL in the CSV file
display_kml_map()
