import folium
import folium.plugins


class Map(folium.Map):
    """A custom Map class that extends folium.Map."""

    def __init__(self, center=(0, 0), zoom=2, **kwargs):
        """Initializes the Map object.

        Args:
            center (tuple, optional): The initial center of the map as (latitude, longitude). Defaults to (0, 0).
            zoom (int, optional): The initial zoom level of the map. Defaults to 2.
            **kwargs: Additional keyword arguments for the folium.Map class.
        """
        super().__init__(location=center, zoom_start=zoom, **kwargs)

    def add_geojson(
        self,
        data,
        zoom_to_layer=True,
        hover_style=None,
        **kwargs,
    ):
        """Adds a GeoJSON layer to the map.

        Args:
            data (str or dict): The GeoJSON data. Can be a file path (str) or a dictionary.
            zoom_to_layer (bool, optional): Whether to zoom to the layer's bounds. Defaults to True.
            hover_style (dict, optional): Style to apply when hovering over features. Defaults to {"color": "yellow", "fillOpacity": 0.2}.
            **kwargs: Additional keyword arguments for the folium.GeoJson layer.

        Raises:
            ValueError: If the data type is invalid.
        """
        import geopandas as gpd

        if hover_style is None:
            hover_style = {"color": "yellow", "fillOpacity": 0.2}

        if isinstance(data, str):
            gdf = gpd.read_file(data)
            geojson = gdf.__geo_interface__
        elif isinstance(data, dict):
            geojson = data

        geojson = folium.GeoJson(data=geojson, **kwargs)
        geojson.add_to(self)

    def add_shp(self, data, **kwargs):
        """Adds a shapefile to the map.

        Args:
            data (str): The file path to the shapefile.
            **kwargs: Additional keyword arguments for the GeoJSON layer.
        """
        import geopandas as gpd

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

    def add_vector(self, data, **kwargs):
        """Adds vector data to the map.

        Args:
            data (str, geopandas.GeoDataFrame, or dict): The vector data. Can be a file path, GeoDataFrame, or GeoJSON dictionary.
            **kwargs: Additional keyword arguments for the GeoJSON layer.

        Raises:
            ValueError: If the data type is invalid.
        """
        import geopandas as gpd

        if isinstance(data, str):
            gdf = gpd.read_file(data)
            self.add_gdf(gdf, **kwargs)
        elif isinstance(data, gpd.GeoDataFrame):
            self.add_gdf(data, **kwargs)
        elif isinstance(data, dict):
            self.add_geojson(data, **kwargs)
        else:
            raise ValueError("Invalid data type")

    def add_layer_control(self):
        """Adds a layer control widget to the map."""
        folium.LayerControl().add_to(self)

    def add_split_map(self, left="openstreetmap", right="cartodbpositron", **kwargs):
        """Add a split map to the folium map. Can handle TIF files.

        Args:
            left (str, optional): basemap for left side. Defaults to "openstreetmap".
            right (str, optional): basemap for right side. Defaults to "cartodbpositron".
        """

        from localtileserver import TileClient, get_folium_tile_layer

        # map_types = {
        #     "ROADMAP": "m",
        #     "SATELLITE": "s",
        #     "HYBRID": "y",
        #     "TERRAIN": "p",
        # }

        # map_type = map_types[map_type.upper()]

        # url = (
        #     f"https://mt1.google.com/vt/lyrs={map_type.lower()}&x={{x}}&y={{y}}&z={{z}}"
        # )
        def _create_layer(source, **kwargs):
            if str(source).lower().endswith((".tif", ".tiff")):
                # Create a TileClient for the raster file
                tile_client = TileClient(source)
                # Generate a Folium tile layer from the TileClient
                return get_folium_tile_layer(tile_client, **kwargs)
            else:
                # Create a standard Folium TileLayer for basemaps
                return folium.TileLayer(source, **kwargs)

        layer_right = _create_layer(right, **kwargs)
        layer_left = _create_layer(left, **kwargs)

        sbs = folium.plugins.SideBySideLayers(
            layer_left=layer_left, layer_right=layer_right
        )

        layer_left.add_to(self)
        layer_right.add_to(self)
        sbs.add_to(self)

    def change_basemap(self, **kwargs):
        """Changes the basemap of the map.

        Args:
            **kwargs: Additional keyword arguments for the folium.TileLayer class.
        """
        from ipywidgets import jslink, Dropdown
        from ipyleaflet import WidgetControl

        # Step 4: Create the dropdown
        data_dict = {
            "OpenStreetMap": "openstreetmap",
            "CartoDB Positron": "cartodbpositron",
            "Stamen Terrain": "stamenterrain",
            "Stamen Toner": "stamentoner",
            "Stamen Watercolor": "stamenwatercolor",
        }
        dropdown = Dropdown(
            options=data_dict,  # keys shown, values returned
            description="Dataset:",
            disabled=False,
        )

        basemap_layer = self.layers[1]
        jslink((dropdown, "value"), (basemap_layer, "basemap"))
        dropdown = WidgetControl(widget=dropdown, position="topright")

        self.add(dropdown)

    def on_dropdown_change(change):
        if change["new"]:
            m.add_basemap(change["new"])
