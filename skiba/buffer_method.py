import ipywidgets as widgets
import geopandas as gpd
import pandas as pd
import geemap as gm
import ee
import os

from skiba.common import get_gee_catalog_as_dict, get_dataset_url, get_dataset_type

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
        # Dropdown - uses cached GEE catalog
        data_dict = get_gee_catalog_as_dict()
        self.dropdown = widgets.Dropdown(
            options=data_dict,
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
                dataset_id = str(change["new"])
                url = get_dataset_url(dataset_id)
                print(f"Selected dataset: {dataset_id}")
                print(f"URL: {url}")

    def on_button_clicked(self, b):
        """
        Callback function to handle button click events.
        """
        import io

        with self.output:
            self.output.clear_output()
            print(
                f"You entered: {self.dropdown.value}. CSV file will be saved to Downloads folder under this name."
            )

            if self.file_upload.value:
                file_info = self.file_upload.value[0]
                content_bytes = file_info["content"].tobytes()
                filename = file_info["name"]
                print(f"Filename: {filename}")

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

            self.extract_median_values(
                data=points, geedata=geedata, start_date=start_date, end_date=end_date
            )

    def extract_median_values(self, data, geedata, start_date, end_date, **kwargs):
        """
        Extracts median values from a GEE dataset for the given geometry.

        Args:
            data (str, pd.DataFrame, gpd.GeoDataFrame): Input data (GeoJSON, DataFrame, or GeoDataFrame).
            geedata (str): GEE dataset ID.
            start_date (str): Start date for filtering the dataset.
            end_date (str): End date for filtering the dataset.
            **kwargs: Additional arguments for the GEE dataset.
        """

        data_type = get_dataset_type(geedata)
        start_date = str(start_date)
        end_date = str(end_date)

        if isinstance(data, str):
            # Assume the file is a GeoJSON or Shapefile with polygons
            gdf = gpd.read_file(data)
            if gdf.crs is None:
                gdf.set_crs("EPSG:4326", inplace=True)
            else:
                gdf = gdf.to_crs("EPSG:4326")
        elif isinstance(data, pd.DataFrame):
            # If you have a DataFrame, it should already have a 'geometry' column with Polygon objects
            # If not, you need to construct it-otherwise, just convert to GeoDataFrame
            gdf = gpd.GeoDataFrame(data, geometry="geometry")
            if gdf.crs is None:
                gdf.set_crs("EPSG:4326", inplace=True)
            else:
                gdf = gdf.to_crs("EPSG:4326")
        else:
            # If already a GeoDataFrame
            if data.crs is None:
                gdf = data.set_crs("EPSG:4326")
            else:
                gdf = data.to_crs("EPSG:4326")

        comp_results = pd.DataFrame()

        for row in gdf.itertuples():
            gdf_row = gdf.iloc[[row.Index]]
            geojson = gdf_row.__geo_interface__
            fc = gm.geojson_to_ee(geojson)

            # Try loading as Image
            if data_type == "image":
                col = ee.Image(geedata)
                col = ee.ImageCollection(col)
            elif data_type == "image_collection":
                col = ee.ImageCollection(geedata)
            else:
                raise ValueError("Dataset ID is not a valid Image or ImageCollection.")

            # If date filters are provided, apply them
            if start_date is not None and end_date is not None:
                col = col.filterDate(start_date, end_date)

            zonal_stats = col.median().reduceRegion(
                reducer=ee.Reducer.median(), geometry=fc.geometry()
            )
            print("Zonal Stats:")
            print(zonal_stats)
            col = zonal_stats.getInfo()
            print(col)

            col = pd.DataFrame.from_dict(col, orient="index")

            print(col)
            print(col.keys())
            print(type(col))

            # col['plot_ID'] = gdf_row['plot_ID'].values[0]
            # col = pd.DataFrame(col)
            comp_results = pd.concat([comp_results, col], axis=0)

        # Load the GEE dataset as an image
        name = geedata
        file_name = name.replace("/", "_")

        out_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        output_file = f"{file_name}.csv"
        out_path = os.path.join(out_dir, output_file)

        # Retrieve data from the image using sampleRegions
        sampled_data = comp_results.to_csv(out_path)
        return sampled_data

        # Try loading as FeatureCollection (convert to raster)

        # Load the GEE dataset as an image
        # geeimage = buffer_method.load_gee_as_image(geedata, start_date, end_date)
        # name = geedata
        # file_name = name.replace("/", "_")

        # out_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        # output_file = f"{file_name}.csv"
        # out_path = os.path.join(out_dir, output_file)

        # # Retrieve data from the image using sampleRegions
        # sampled_data = gm.zonal_statistics(geeimage, fc, out_path, stat_type="MEDIAN")

        # return sampled_data

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
        """
        Creates a date picker widget for selecting dates.

        Returns:
            ipywidgets.DatePicker: A date picker widget for selecting dates."""
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
        data_type = get_dataset_type(dataset_id)
        start_date = str(start_date)
        end_date = str(end_date)

        if data_type == "image":
            img = ee.Image(dataset_id)
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
