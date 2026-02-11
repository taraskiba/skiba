"""The common module contains common functions and classes used by the other modules."""

from functools import lru_cache

import requests


GEE_CATALOG_URL = "https://raw.githubusercontent.com/opengeos/geospatial-data-catalogs/master/gee_catalog.json"


def hello_world():
    """Prints "Hello World!" to the console."""
    print("Hello World!")


@lru_cache(maxsize=1)
def fetch_gee_catalog():
    """
    Fetch and cache the Google Earth Engine dataset catalog.

    The catalog is fetched once and cached for the lifetime of the session,
    avoiding repeated network requests on every operation.

    Returns:
        list: List of dataset dictionaries from the GEE catalog, or None if fetch fails.
    """
    try:
        response = requests.get(GEE_CATALOG_URL, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Error connecting to the server: {conn_err}")
    except requests.exceptions.Timeout:
        print("Request timed out while fetching GEE catalog")
    except Exception as err:
        print(f"An error occurred: {err}")
    return None


def get_gee_catalog_as_dict(key_field="title", value_field="id"):
    """
    Get the GEE catalog as a dictionary for dropdown menus.

    Args:
        key_field: Field to use as dictionary keys (default: "title")
        value_field: Field to use as dictionary values (default: "id")

    Returns:
        dict: Dictionary mapping key_field to value_field for each catalog item.
    """
    catalog = fetch_gee_catalog()
    if catalog is None:
        return {}
    return {
        item[key_field]: item[value_field]
        for item in catalog
        if key_field in item and value_field in item
    }


def get_dataset_type(dataset_id):
    """
    Get the type of a GEE dataset (image, image_collection, etc).

    Args:
        dataset_id: The GEE dataset ID to look up.

    Returns:
        str: The dataset type, or None if not found.
    """
    catalog = fetch_gee_catalog()
    if catalog is None:
        return None
    for item in catalog:
        if item.get("id") == dataset_id:
            return item.get("type")
    return None


def get_dataset_url(dataset_id):
    """
    Get the documentation URL for a GEE dataset.

    Args:
        dataset_id: The GEE dataset ID to look up.

    Returns:
        str: The dataset URL, or None if not found.
    """
    catalog = fetch_gee_catalog()
    if catalog is None:
        return None
    for item in catalog:
        if item.get("id") == dataset_id:
            return item.get("url")
    return None
