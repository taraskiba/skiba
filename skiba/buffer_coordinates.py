import requests
import ipywidgets as widgets
import geopandas as gpd
import pandas as pd
import geemap as gm
from shapely.geometry import Point
import shapely
from pyproj import Transformer
import json
import os
import numpy as np

# ee.Authenticate()
# ee.Initialize(project="ee-forestplotvariables")


class buffer_coordinates:
    def __init__(self):
        """
        Initializes the buffer_coordinates class and sets up the GUI components.
        Part 1 of buffered coordinates approach which creates circles around points.
        (Part 2 is in buffer_method.py)
        """
        # File Upload
        self.file_upload = widgets.FileUpload(
            accept=".csv, .txt",  # Accepted file extension e.g. '.txt', '.pdf', 'image/*', 'image/*,.pdf'
            multiple=False,  # True to accept multiple files upload else False
        )

        # Dropdown
        url = "https://raw.githubusercontent.com/opengeos/geospatial-data-catalogs/master/gee_catalog.json"
        data = self.fetch_geojson(url)
        data_dict = {item["title"]: item["id"] for item in data if "title" in item}
        self.dropdown = widgets.Dropdown(
            options=data_dict,  # keys shown, values returned
            description="Dataset:",
            disabled=False,
        )
        self.dropdown.observe(self.on_dropdown_change, names="value")

        self.buffer_radius = widgets.FloatText(
            value=10,
            description="Buffer radius (ft):",
            disabled=False,
            display="flex",
            flex_flow="column",
            align_items="stretch",
            style={"description_width": "initial"},
        )

        self.run_button = widgets.Button(
            description="Run Query",
            disabled=False,
            button_style="",  # 'success', 'info', 'warning', 'danger' or ''
            tooltip="Click me",
            icon="rotate right",  # (FontAwesome names without the `fa-` prefix)
        )

        self.output = widgets.Output()

        self.run_button.on_click(self.on_button_clicked)

        self.hbox = widgets.HBox(
            [self.file_upload, self.dropdown, self.buffer_radius, self.run_button]
        )

        self.vbox = widgets.VBox([self.hbox, self.output])

    def on_button_clicked(self, b):
        """
        Callback function to handle button click events."""
        with self.output:
            self.output.clear_output()
            print(
                f"GeoJSON file will be saved to Downloads folder under this name:{self.buffer_radius.value}.0.geojson"
            )

            import io

            if self.file_upload.value:
                # For the first file (if multiple=False)
                file_info = self.file_upload.value[0]
                content_bytes = file_info["content"].tobytes()  # file content as bytes
                filename = file_info["name"]
                print(f"Filename: {filename}")
                points = pd.read_csv(io.BytesIO(content_bytes))
            else:
                print("Please upload a CSV file.")

            radius_ft = self.buffer_radius.value

            out_dir = os.path.join(os.path.expanduser("~"), "Downloads")
            output_file = f"{radius_ft}.geojson"
            out_path = os.path.join(out_dir, output_file)

            self.obfuscate_points_to_circles(
                data=points,
                radius_feet=radius_ft,
                plot_id_col="plot_ID",
                output_file=out_path,
            )
            print(f"Buffered coordinates GeoJSON saved to {out_path}")

    def on_dropdown_change(self, change):
        """
        Callback function to handle dropdown value changes.
        """
        if change["new"]:
            with self.output:
                self.output.clear_output()
                catalog = "https://raw.githubusercontent.com/opengeos/geospatial-data-catalogs/master/gee_catalog.json"
                data = self.fetch_geojson(catalog)
                data_dict = {item["id"]: item["url"] for item in data if "id" in item}
                change_value = str(change["new"])
                url = data_dict.get(change_value)
                print(f"Selected dataset: {change['new']}")
                print(f"URL: {url}")

    def create_obfuscated_circle(self, point, radius_feet, crs="EPSG:4326"):
        """
        Create a circle polygon (as a shapely geometry) with the given radius in feet,
        where the provided point is randomly located inside the circle (not at the center).
        """
        # Convert radius from feet to meters
        radius_m = radius_feet * 0.3048

        # Project to local UTM for accurate distance calculations
        utm_crs = f"EPSG:326{int((point.x + 180) // 6) + 1}"
        transformer_to_utm = Transformer.from_crs(crs, utm_crs, always_xy=True)
        transformer_to_latlon = Transformer.from_crs(utm_crs, crs, always_xy=True)
        x, y = transformer_to_utm.transform(point.x, point.y)

        # Randomize the point's location within the circle
        angle = np.random.uniform(0, 2 * np.pi)
        distance = np.random.uniform(0, radius_m)
        # Calculate center of the circle so that the point is inside the circle but not at the center
        center_x = x - distance * np.cos(angle)
        center_y = y - distance * np.sin(angle)
        center = Point(center_x, center_y)

        # Create the circle at the calculated center
        circle = center.buffer(radius_m, resolution=32)

        # Transform the circle back to WGS84
        circle_latlon = shapely.ops.transform(
            lambda x, y: transformer_to_latlon.transform(x, y), circle
        )
        return circle_latlon

    def obfuscate_points_to_circles(self, data, radius_feet, plot_id_col, output_file):
        """
        Obfuscate points to circles and save as GeoJSON.

        Args:
            data (str, pd.DataFrame, gpd.GeoDataFrame): Input data (GeoJSON, DataFrame, or GeoDataFrame).
            radius_feet (float): Radius of the circle in feet.
            plot_id_col (str): Column name for plot IDs.
            output_file (str): Path to save the output GeoJSON file.
        """
        if isinstance(data, str):
            coordinates = pd.read_csv(data)
            gdf = gpd.GeoDataFrame(
                coordinates,
                geometry=gpd.points_from_xy(coordinates.LON, coordinates.LAT),
                crs="EPSG:4326",  # Directly set CRS during creation
            )
        elif isinstance(data, pd.DataFrame):
            coordinates = data
            gdf = gpd.GeoDataFrame(
                coordinates,
                geometry=gpd.points_from_xy(coordinates.LON, coordinates.LAT),
                crs="EPSG:4326",  # Directly set CRS during creation
            )
        else:
            gdf = data.to_crs(epsg=4326)  # Ensure WGS84

        circles = []
        ids = []
        for idx, row in gdf.iterrows():
            point = row["geometry"]
            circle = self.create_obfuscated_circle(point, radius_feet, crs=gdf.crs)
            circles.append(circle)
            ids.append(row[plot_id_col])
        # Create new GeoDataFrame
        gdf_circles = gpd.GeoDataFrame(
            {plot_id_col: ids, "geometry": circles}, crs=gdf.crs
        )
        geojson_str = gdf_circles.to_json()
        with open(output_file, "w") as f:
            f.write(geojson_str)
        print(f"GeoJSON saved to {output_file}")
        return gdf_circles

    def fetch_geojson(self, url):
        """
        Fetch GeoJSON data from a given URL.

        Args:
            url (str): URL to fetch the GeoJSON data from.
        """
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raises an exception for HTTP errors
            geojson_data = response.json()  # Parse the JSON response
            return geojson_data
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except requests.exceptions.ConnectionError as conn_err:
            print(f"Error connecting to the server: {conn_err}")
        except Exception as err:
            print(f"An error occurred: {err}")
        return None
