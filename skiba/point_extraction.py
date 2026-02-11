import ipywidgets as widgets
import geopandas as gpd
import pandas as pd
import geemap as gm
import ee
import os

from skiba.common import get_gee_catalog_as_dict, get_dataset_url, get_dataset_type

# ee.Authenticate()
# ee.Initialize(project="ee-forestplotvariables")


class PointExtraction:
    def __init__(self):
        # File Upload
        self.file_upload = widgets.FileUpload(
            accept=".csv, .txt",  # Accepted file extension e.g. '.txt', '.pdf', 'image/*', 'image/*,.pdf'
            multiple=False,  # True to accept multiple files upload else False
        )
        # Dropdown - uses cached GEE catalog
        data_dict = get_gee_catalog_as_dict()
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
                dataset_id = str(change["new"])
                url = get_dataset_url(dataset_id)
                print(f"Selected dataset: {dataset_id}")
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
                points = pd.read_csv(io.BytesIO(content_bytes))
                lat_cols = ["lat", "latitude", "y", "LAT", "Latitude", "Lat", "Y"]
                lon_cols = [
                    "lon",
                    "long",
                    "longitude",
                    "x",
                    "LON",
                    "Longitude",
                    "Long",
                    "X",
                ]
                id_cols = ["id", "ID", "plot_ID", "plot_id", "plotID", "plotId"]

                def find_column(possible_names, columns):
                    for name in possible_names:
                        if name in columns:
                            return name
                    # fallback: check case-insensitive match
                    lower_columns = {c.lower(): c for c in columns}
                    for name in possible_names:
                        if name.lower() in lower_columns:
                            return lower_columns[name.lower()]
                    raise ValueError(f"No matching column found for {possible_names}")

                lat_col = find_column(lat_cols, points.columns)
                lon_col = find_column(lon_cols, points.columns)
                id_col = find_column(id_cols, points.columns)
                points = points.rename(
                    columns={lat_col: "LAT", lon_col: "LON", id_col: "plot_ID"}
                )
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
        geeimage = PointExtraction.load_gee_as_image(geedata, start_date, end_date)
        name = f"{geedata}"
        file_name = name.replace("/", "_")
        out_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        output_file = f"{file_name}.csv"
        out_path = os.path.join(out_dir, output_file)
        # Retrieve data from the image using sampleRegions
        sampled_data = gm.extract_values_to_points(fc, geeimage, out_path)
        return sampled_data

    def create_dropdown():
        """
        Creates an ipywidgets dropdown menu from the cached GEE catalog.

        Returns:
            ipywidgets.Dropdown: A dropdown widget with dataset names from the catalog.
        """
        data_dict = get_gee_catalog_as_dict()
        dropdown = widgets.Dropdown(
            options=data_dict,
            description="Dataset:",
            disabled=False,
        )
        return dropdown

    def add_date_picker():
        date_picker = widgets.DatePicker(description="Pick a Date", disabled=False)
        return date_picker

    def load_gee_as_image(dataset_id, start_date, end_date, **kwargs):
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
        data_type = get_dataset_type(dataset_id)
        start_date = str(start_date)
        end_date = str(end_date)

        if data_type == "image":
            img = ee.Image(dataset_id)
            img.getInfo()
            return img
        elif data_type == "image_collection":
            col = ee.ImageCollection(dataset_id)
            # If date filters are provided, apply them
            if start_date is not None and end_date is not None:
                col = col.filterDate(start_date, end_date)
            # Reduce to a single image (e.g., median composite)
            img = col.median()
            return img
        else:
            raise ValueError("Dataset ID is not a valid Image or ImageCollection.")
