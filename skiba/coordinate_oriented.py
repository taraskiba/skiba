import pandas as pd
import geopandas as gpd
import geemap as gm


def get_coordinate_data(data, geedata, start_date, end_date, **kwargs):
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
    geeimage = load_gee_as_image(geedata, start_date, end_date)

    name = geedata
    file_name = name.replace("/", "_")

    output = f"{file_name}.csv"

    # Retrieve data from the image using sampleRegions
    sampled_data = gm.extract_values_to_points(fc, geeimage, output)

    return sampled_data


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
