import requests
import ipywidgets as widgets
import geopandas as gpd
import pandas as pd
import geemap as gm
import ee
import os

# ee.Authenticate()
# ee.Initialize(project="ee-forestplotvariables")


class data_process:
    def __init__(self):
        # File Upload
        self.file_upload = widgets.FileUpload(
            accept=".csv, .txt",  # Accepted file extension e.g. '.txt', '.pdf', 'image/*', 'image/*,.pdf'
            multiple=False,  # True to accept multiple files upload else False
        )
        # Dropdown
        url = "https://raw.githubusercontent.com/opengeos/geospatial-data-catalogs/master/gee_catalog.json"
        data = data_process.fetch_geojson(url)
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
            icon="rotate right",  # (FontAwesome names without the `fa-` prefix)
        )

        self.output = widgets.Output()

        self.run_button.on_click(self.on_button_clicked)
        self.dropdown.observe(self.on_dropdown_change, names="value")

        self.hbox = widgets.HBox(
            [
                self.file_upload,
                self.dropdown,
                self.start_date,
                self.end_date,
                self.run_button,
            ]
        )
        self.vbox = widgets.VBox([self.hbox, self.output])

    def on_dropdown_change(self, change):
        if change["new"]:
            with self.output:
                self.output.clear_output()
                catalog = "https://raw.githubusercontent.com/opengeos/geospatial-data-catalogs/master/gee_catalog.json"
                data = data_process.fetch_geojson(catalog)
                data_dict = {item["id"]: item["url"] for item in data if "id" in item}
                change_value = str(change["new"])
                url = data_dict.get(change_value)
                print(f"Selected dataset: {change['new']}")
                print(f"URL: {url}")

    def on_button_clicked(self, b):
        with self.output:
            self.output.clear_output()
            print(
                f"You entered: {self.dropdown.value}. CSV file will be saved to Downloads folder under this name."
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

            geedata = self.dropdown.value
            start_date = self.start_date.value
            end_date = self.end_date.value

            self.get_coordinate_data(
                data=points, geedata=geedata, start_date=start_date, end_date=end_date
            )

    def get_coordinate_data(self, data, geedata, start_date, end_date, **kwargs):
        """
        Pull data from provided coordinates from GEE.

        Args:
            data (str): The data to get the coordinate data from.

        Returns:
            data (str): CSV file contained GEE data.
        """

        # Load data with safety checks
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

        geojson = gdf.__geo_interface__
        fc = gm.geojson_to_ee(geojson)

        # Load the GEE dataset as an image
        geeimage = data_process.load_gee_as_image(geedata, start_date, end_date)

        name = geedata
        file_name = name.replace("/", "_")

        out_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        output_file = f"{file_name}.csv"
        out_path = os.path.join(out_dir, output_file)

        # Retrieve data from the image using sampleRegions
        sampled_data = gm.extract_values_to_points(fc, geeimage, out_path)

        return sampled_data

    def fetch_geojson(url):
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

        data = data_process.fetch_geojson(url)

        data_dict = {item["title"]: item["id"] for item in data if "title" in item}

        dropdown = widgets.Dropdown(
            options=data_dict,  # keys shown, values returned
            description="Dataset:",
            disabled=False,
        )

        return dropdown

    def add_date_picker():
        date_picker = widgets.DatePicker(description="Pick a Date", disabled=False)

        return date_picker

    def load_gee_as_image(dataset_id, start_date=None, end_date=None, **kwargs):
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
            # If .getInfo() doesn't throw, it's an Image
            img.getInfo()
            return img
        except Exception:
            pass

        # Try loading as ImageCollection
        try:
            col = ee.ImageCollection(dataset_id)
            # If date filters are provided, apply them
            if start_date and end_date:
                col = col.filterDate(start_date, end_date)
            else:
                pass
            # Reduce to a single image (e.g., median composite)
            img = col.median()
            img.getInfo()  # Throws if not valid
            return img
        except Exception:
            pass

        # Try loading as FeatureCollection (convert to raster)
        try:
            fc_temp = ee.FeatureCollection(dataset_id)
            # Convert to raster: burn a value of 1 into a new image
            img = fc_temp.reduceToImage(properties=[], reducer=ee.Reducer.constant(1))
            img.getInfo()
            return img
        except Exception:
            raise ValueError(
                "Dataset ID is not a valid Image, ImageCollection, or FeatureCollection."
            )
