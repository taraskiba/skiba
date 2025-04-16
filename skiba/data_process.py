import requests
import json
import ipywidgets as widgets
import geopandas as gpd
import pandas as pd
import geemap as gm
import ee
import os

ee.Initialize(project="ee-forestplotvariables")
ee.Authenticate()


class data_process:
    def __init__(self, data, **kwargs):
        self.data = data
        for key, value in kwargs.items():
            setattr(self, key, value)

    def create_dropdown():
        """
        Creates an ipywidgets dropdown menu from a GeoJSON catalog.

        Args:
            url (str, optional): URL to the GeoJSON catalog. Defaults to the Opengeos catalog.

        Returns:
            ipywidgets.Dropdown: A dropdown widget with the names from the catalog.
        """

        url = "https://github.com/opengeos/geospatial-data-catalogs/blob/master/gee_catalog.json"

        data = "../data/gee_catalog.json"
        with open(data, "r") as file:
            data = json.load(file)

        data_dict = {item["title"]: item["id"] for item in data if "title" in item}

        # Step 4: Create the dropdown
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
            fc = ee.FeatureCollection(dataset_id)
            # Convert to raster: burn a value of 1 into a new image
            img = fc.reduceToImage(properties=[], reducer=ee.Reducer.constant(1))
            img.getInfo()
            return img
        except Exception:
            raise ValueError(
                "Dataset ID is not a valid Image, ImageCollection, or FeatureCollection."
            )

    def get_coordinate_data(data, geedata, **kwargs):
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
        else:
            gdf = data.to_crs(epsg=4326)  # Ensure WGS84

        geojson = gdf.__geo_interface__
        fc = gm.geojson_to_ee(geojson)

        # Load the GEE dataset as an image
        geeimage = data_process.load_gee_as_image(geedata)

        # Retrieve data from the image using sampleRegions
        sampled_data = geeimage.sampleRegions(
            collection=fc,
            scale=geeimage.projection().nominalScale(),  # Adjust scale based on dataset resolution
            geometries=True,  # Include geometry in the output
        )

        return sampled_data
