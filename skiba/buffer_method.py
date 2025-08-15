import requests
import ipywidgets as widgets
import geopandas as gpd
import pandas as pd
import geemap as gm
import ee
import os
import json

# ee.Authenticate()
# ee.Initialize(project="ee-forestplotvariables")


class buffer_method:
    def __init__(self):
        """
        Initializes the buffer_method class and sets up the GUI components.
        Part 2 of buffered coordinates approach which accesses GEE datasets and extracts median values.
        (Part 1 is in buffer_coordinates.py)
        """
        # File Upload
        self.file_upload = widgets.FileUpload(
            accept=".geojson",  # Accepted file extension e.g. '.txt', '.pdf', 'image/*', 'image/*,.pdf'
            multiple=False,  # True to accept multiple files upload else False
        )
        # Dropdown
        url = "https://raw.githubusercontent.com/opengeos/geospatial-data-catalogs/master/gee_catalog.json"
        data = buffer_method.fetch_geojson(url)
        data_dict = {item["title"]: item["id"] for item in data if "title" in item}
        self.dropdown = widgets.Dropdown(
            options=data_dict,  # keys shown, values returned
            description="Dataset:",
            disabled=False,
        )

        self.start_date = widgets.DatePicker(description="Start Date", disabled=False)
        self.end_date = widgets.DatePicker(description="End Date", disabled=False)

        self.run_button = widgets.Button(
            description="Run Query",
            disabled=False,
            button_style="",  # 'success', 'info', 'warning', 'danger' or ''
            tooltip="Click me",
            icon="check",  # (FontAwesome names without the `fa-` prefix)
        )

        self.output = widgets.Output()

        self.run_button.on_click(self.on_button_clicked)
        self.dropdown.observe(self.on_dropdown_change, names="value")

        self.hbox = widgets.HBox([self.file_upload, self.dropdown])

        self.hbox_bottom = widgets.HBox(
            [self.start_date, self.end_date, self.run_button]
        )
        self.vbox = widgets.VBox([self.hbox, self.hbox_bottom, self.output])

    def on_dropdown_change(self, change):
        """
        Callback function to handle dropdown value changes."""
        if change["new"]:
            with self.output:
                self.output.clear_output()
                catalog = "https://raw.githubusercontent.com/opengeos/geospatial-data-catalogs/master/gee_catalog.json"
                data = buffer_method.fetch_geojson(catalog)
                data_dict = {item["id"]: item["url"] for item in data if "id" in item}
                change_value = str(change["new"])
                url = data_dict.get(change_value)
                print(f"Selected dataset: {change['new']}")
                print(f"URL: {url}")

    def on_button_clicked(self, b):
        """
        Callback function to handle button click events.
        """
        import io

        with self.output:
            self.output.clear_output()
            print(f"You entered: {self.dropdown.value}.")

            if self.file_upload.value:
                file_info = self.file_upload.value[0]
                content_bytes = file_info["content"].tobytes()
                name = file_info["name"]
                file_name = name.replace("/", "_")
                print(f"Your file will be saved under {file_name}.csv")

                # --- Modification: Read GeoJSON from bytes ---
                # Use BytesIO to read the uploaded GeoJSON file
                geojson_buffer = io.BytesIO(content_bytes)
                points = gpd.read_file(geojson_buffer)
            else:
                print("Please upload a GeoJSON file.")
                return

            geedata = self.dropdown.value
            start_date = self.start_date.value
            end_date = self.end_date.value

            out_dir = os.path.join(os.path.expanduser("~"), "Downloads")
            output_file = f"{file_name}.csv"
            out_path = os.path.join(out_dir, output_file)

            extracted_results = self.extract_median_values(
                data=points, geedata=geedata, start_date=start_date, end_date=end_date
            )

            returned_csv = gm.ee_to_csv(extracted_results, filename=out_path)

            return returned_csv

    def extract_median_values(
        self, data, geedata, start_date=None, end_date=None, **kwargs
    ):
        """
        Extracts median values from a GEE dataset for the given geometry.

        Args:
            data (str, pd.DataFrame, gpd.GeoDataFrame): Input data (GeoJSON, DataFrame, or GeoDataFrame).
            geedata (str): GEE dataset ID.
            start_date (str): Start date for filtering the dataset.
            end_date (str): End date for filtering the dataset.
            **kwargs: Additional arguments for the GEE dataset.
        """

        # Convert GeoDataFrame to GeoJSON dictionary (to feed into Earth Engine)
        geojson_dict = json.loads(data.to_json())
        geojson_object = gm.geojson_to_ee(geojson_dict)

        # Define your dataset and time range, e.g. Sentinel-2 in 2022
        geeimage = buffer_method.load_gee_as_image(geedata, start_date, end_date)

        # Extract median values over each polygon using reduceRegions
        results = geeimage.sampleRegions(
            collection=geojson_object, geometries=True, scale=10
        )

        return results

    def load_gee_as_image(self, dataset_id, start_date=None, end_date=None, **kwargs):
        """
        Loads any GEE dataset (Image, ImageCollection, FeatureCollection) as an ee.Image.
        Optionally filters by start and end date if applicable.

        Parameters:
            dataset_id (str): The Earth Engine dataset ID.
            start_date (str): Optional start date in 'YYYY-MM-DD' format.
            end_date (str): Optional end date in 'YYYY-MM-DD' format.

        Returns:
            ee.Image: The resulting image.
        """
        # Try loading as Image
        try:
            img = ee.Image(dataset_id)
            img.getInfo()  # validate image
            return img
        except Exception:
            pass

        # Try loading as ImageCollection
        try:
            col = ee.ImageCollection(dataset_id)
            if start_date and end_date:
                col = col.filterDate(start_date, end_date)
            # Reduce to median image
            img = col.median()
            img.toBands()  # validate
            return img
        except Exception:
            pass

        # Try loading as FeatureCollection (convert to raster mask)
        try:
            col = ee.FeatureCollection(dataset_id)
            if start_date and end_date:
                col = col.filterDate(start_date, end_date)
            img = col.reduceToImage(properties=[], reducer=ee.Reducer.median())
            img.getInfo()
            return img
        except Exception:
            raise ValueError(
                "Dataset ID is not a valid Image, ImageCollection, or FeatureCollection."
            )

    def fetch_geojson(url):
        """
        Fetches GeoJSON data from a given URL.

        Args:
            url (str): URL to the GeoJSON file."""
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

    def create_dropdown():
        """
        Creates an ipywidgets dropdown menu from a GeoJSON catalog.

        Args:
            url (str, optional): URL to the GeoJSON catalog. Defaults to the Opengeos catalog.

        Returns:
            ipywidgets.Dropdown: A dropdown widget with the names from the catalog.
        """

        url = "https://raw.githubusercontent.com/opengeos/geospatial-data-catalogs/master/gee_catalog.json"

        data = buffer_method.fetch_geojson(url)

        data_dict = {item["title"]: item["id"] for item in data if "title" in item}

        dropdown = widgets.Dropdown(
            options=data_dict,  # keys shown, values returned
            description="Dataset:",
            disabled=False,
        )

        return dropdown

    def add_date_picker():
        """
        Creates a date picker widget for selecting dates.

        Returns:
            ipywidgets.DatePicker: A date picker widget for selecting dates."""
        date_picker = widgets.DatePicker(description="Pick a Date", disabled=False)

        return date_picker
