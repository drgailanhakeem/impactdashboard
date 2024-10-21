# Install necessary libraries
!pip install fastkml folium

# Import necessary libraries
import requests
from fastkml import kml
import folium
from shapely.geometry import Point, Polygon, LineString

# URL of the KML file (use the correct link if it's publicly accessible)
kml_url = 'https://www.google.com/maps/d/kml?mid=1W-Ks4l29dKSsXIo28FJN-fEd7lOnq10'

# Send a request to download the KML data
response = requests.get(kml_url)

# Check if the response is valid
if response.status_code == 200:
    try:
        # Save the KML data to a file
        kml_file_path = '/content/map_data.kml'
        with open(kml_file_path, 'wb') as f:
            f.write(response.content)

        print(f"KML file downloaded and saved to {kml_file_path}")
        
        # Attempt to open the file using ISO-8859-1 encoding if UTF-8 fails
        with open(kml_file_path, 'r', encoding='iso-8859-1') as f:
            kml_data = f.read()

        # Parse the KML content
        k = kml.KML()
        k.from_string(kml_data)

        # Create a map object centered on a default location (this will be updated later)
        map_center = [35.0, 45.0]
        m = folium.Map(location=map_center, zoom_start=8)

        # Extracting the data from KML and add it to the map
        features = list(k.features())
        for feature in features:
            if hasattr(feature, 'geometry'):
                geom = feature.geometry

                # Handle different types of geometries
                if isinstance(geom, Point):
                    # Add a marker for the point
                    coords = geom.coords[0]
                    folium.Marker([coords[1], coords[0]], popup=feature.name).add_to(m)

                elif isinstance(geom, LineString):
                    # Add a polyline for the LineString
                    coords = [[point[1], point[0]] for point in geom.coords]
                    folium.PolyLine(coords, color="blue", weight=2.5, opacity=1).add_to(m)

                elif isinstance(geom, Polygon):
                    # Add a polygon to the map
                    coords = [[point[1], point[0]] for point in geom.exterior.coords]
                    folium.Polygon(coords, color="green", fill=True, fill_opacity=0.4).add_to(m)

                # Update map center to the first feature's coordinates
                if isinstance(geom, (Point, LineString, Polygon)):
                    map_center = [coords[0][1], coords[0][0]]
                    m.location = map_center

        # Display the map
        m

    except Exception as e:
        print(f"Error processing the KML file: {e}")
else:
    print(f"Failed to retrieve the KML data. Status code: {response.status_code}")
