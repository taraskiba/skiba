"""Main module."""

import os
import ipyleaflet


class Map(ipyleaflet.Map):
    def __init__(self, center=[40, 100], zoom=4, height="500px", **kwargs):
        super().__init__(center=center, zoom=zoom, height=height, **kwargs)
        self.layout.height = height
        self.scroll_wheel_zoom = True

    def add_basemap(self, basemap="OpenStreetMap"):
        """Add basemap to the map.

        Args:
            basemap (str, optional): Basemap name. Starts with "OpenStreetMap".
        """

        url = eval(f"ipyleaflet.basemaps.{basemap}").build_url()
        layer = ipyleaflet.TileLayer(url=url, name=basemap)
        self.add(layer)

    def add_layer_Control(self):
        """Add layer control to the map."""
        self.add(ipyleaflet.LayersControl(position="topright"))

    def add_vector(self, data, **kwargs):
        """Add vector layer to the map.

        Args:
            data (str, geopandas.GeoDataFrame, or dict): file path, GeoDataFrame, or dictionary allowed.
            **kwargs: Additional arguments for the layer.

        Returns:
            ValueError(f"File {data} not found."
        """

        import geopandas as gpd

        if os.path.exists(data):
            if isinstance(data, str):
                data = gpd.read_file(data)
                self.add_gdf(data, **kwargs)
            elif isinstance(data, gpd.GeoDataFrame):
                self.add_gdf(data, **kwargs)
            elif isinstance(data, dict):
                self.add_geojson(data, **kwargs)
        else:
            raise ValueError(f"File {data} not found.")
