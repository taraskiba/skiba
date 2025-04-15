import requests
import json
import ipywidgets as widgets


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
