import geemap as gm
import ipyleaflet
import ipywidgets as widgets
import geopandas as gpd
import pandas as pd

# import os

# This code adds various widgets to the map for user interaction.


class Map(ipyleaflet.Map):

    def __init__(self, center=[37.5, -95], zoom=4, height="600px", **kwargs):

        super().__init__(center=center, zoom=zoom, **kwargs)
        self.layout.height = height
        self.scroll_wheel_zoom = True

    def add_basemap(self, basemap="Esri.WorldImagery"):
        """Add basemap to the map.

        Args:
            basemap (str, optional): Basemap name. Defaults to "Esri.WorldImagery".
        """

        url = eval(f"ipyleaflet.basemaps.{basemap}").build_url()
        layer = ipyleaflet.TileLayer(url=url, name=basemap)
        self.add(layer)

    def add_geojson(
        self,
        data,
        hover_style=None,
        **kwargs,
    ):
        """Adds a GeoJSON layer to the map.

        Args:
            data (str or dict): The GeoJSON data. Can be a file path (str) or a dictionary.
            zoom_to_layer (bool, optional): Whether to zoom to the layer's bounds. Defaults to True.
            hover_style (dict, optional): Style to apply when hovering over features. Defaults to {"color": "yellow", "fillOpacity": 0.2}.
            **kwargs: Additional keyword arguments for the ipyleaflet.GeoJSON layer.

        Raises:
            ValueError: If the data type is invalid.
        """
        import geopandas as gpd

        if hover_style is None:
            hover_style = {"color": "gray", "fillOpacity": 0.2}

        if isinstance(data, str):
            gdf = gpd.read_file(data)
            geojson = gdf.__geo_interface__
        elif isinstance(data, dict):
            geojson = data

        style = {"color": "black", "weight": 1, "opacity": 1}

        layer = ipyleaflet.GeoJSON(
            data=geojson, hover_style=hover_style, style=style, **kwargs
        )
        self.add_layer(layer)

    def add_points(self, data, **kwargs):
        """Adds points to the map.

        Args:
            data (str or dict): The GeoJSON data. Can be a file path (str) or a dictionary.
            **kwargs: Additional keyword arguments for the ipyleaflet.GeoJSON layer.
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

        point_style = {
            "radius": 5,
            "fillOpacity": 1,
            "fillColor": "white",
            "weight": 1,
        }  # 'color': 'white',

        geo_data = ipyleaflet.GeoData(
            geo_dataframe=gdf,
            point_style=point_style,
        )

        self.add(geo_data)

    def add_shp(self, data, **kwargs):
        """Adds a shapefile to the map.

        Args:
            data (str): The file path to the shapefile.
            **kwargs: Additional keyword arguments for the GeoJSON layer.
        """

        gdf = gpd.read_file(data)
        gdf = gdf.to_crs(epsg=4326)
        geojson = gdf.__geo_interface__
        self.add_geojson(geojson, **kwargs)

    def add_gdf(self, gdf, **kwargs):
        """Adds a GeoDataFrame to the map.

        Args:
            gdf (geopandas.GeoDataFrame): The GeoDataFrame to add.
            **kwargs: Additional keyword arguments for the GeoJSON layer.
        """
        gdf = gdf.to_crs(epsg=4326)
        geojson = gdf.__geo_interface__
        self.add_geojson(geojson, **kwargs)

    def add_widgets(self):
        """Creates and displays widgets for user interaction."""

        from ipywidgets import jslink, FloatSlider
        from ipyleaflet import WidgetControl

        # date_picker = widgets.DatePicker(description="Pick a Date", disabled=False)
        opacity_slider = widgets.FloatSlider(
            value=1,
            min=0,
            max=1.0,
            step=0.01,
            description="Opacity",
            continuous_update=False,
            orientation="horizontal",
            readout=True,
            readout_format=".2f",
            style={"description_width": "initial"},
        )

        basemap_layer = self.layers[1]
        jslink((opacity_slider, "value"), (basemap_layer, "opacity"))
        opacity_control = WidgetControl(widget=opacity_slider, position="topright")

        # jslink((date_picker, "value"), (self, "date"))
        # date_control = WidgetControl(widget = date_picker, position="bottomright")

        self.add(opacity_control)
        # self.add(date_control)

    # Using geemap, ipyleaflet, and ipywidgets create a map with a dropdown menu that has any Google Earth Engine dataset
