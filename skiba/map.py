import ipyleaflet
import ipywidgets as widgets
import geopandas as gpd
import pandas as pd
import geemap as gm

# import os

# This code adds various widgets to the map for user interaction.


class Map(ipyleaflet.Map):

    def __init__(self, center=[37.5, -95], zoom=4, height="600px", **kwargs):

        super().__init__(center=center, zoom=zoom, **kwargs)
        self.layout.height = height
        self.scroll_wheel_zoom = True
        self.add_layer_control()
        self.change_basemap()
        self.add_search_marker()
        self.upload_points()

    def add_basemap(self, basemap="Esri.WorldImagery"):
        """Add basemap to the map.

        Args:
            basemap (str, optional): Basemap name. Defaults to "Esri.WorldImagery".
        """

        url = eval(f"ipyleaflet.basemaps.{basemap}").build_url()
        layer = ipyleaflet.TileLayer(url=url, name=basemap)
        self.add(layer)

    def add_google_map(self, map_type="ROADMAP"):
        """Add Google Map to the map.

        Args:
            map_type (str, optional): Map type. Defaults to "ROADMAP".
        """
        map_types = {
            "ROADMAP": "m",
            "SATELLITE": "s",
            "HYBRID": "y",
            "TERRAIN": "p",
        }
        map_type = map_types[map_type.upper()]

        url = (
            f"https://mt1.google.com/vt/lyrs={map_type.lower()}&x={{x}}&y={{y}}&z={{z}}"
        )
        layer = ipyleaflet.TileLayer(url=url, name="Google Map")
        self.add(layer)

    def add_layer_control(self):
        """Adds a layer control widget to the map."""
        control = ipyleaflet.LayersControl(position="topright")
        self.add_control(control)

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
        elif isinstance(data, pd.DataFrame):
            coordinates = data
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

    def upload_points(self, **kwargs):
        """Uploads points to the map."""

        from ipywidgets import FileUpload, Button, ToggleButton, HBox

        self.button = Button(
            description="Add Points",
            disabled=False,
            button_style="",  # 'success', 'info', 'warning', 'danger' or ''
            tooltip="Click me",
            icon="regular circle dot",  # (FontAwesome names without the `fa-` prefix)
        )

        self.file_upload = FileUpload(
            accept=".csv",
            multiple=False,
            description="Upload CSV",
            style={"description_width": "initial"},
        )

        self.close_button = ToggleButton(
            icon="times", value=True, tooltip="Close upload control"
        )
        self.close_button.layout = widgets.Layout(width="38px", height="38px")

        self.hbox = HBox([self.file_upload, self.button, self.close_button])

        is_open = [True]

        self.close_button.observe(self.on_toggle_change, names="value")

        self.button.on_click(self.on_button_clicked)

        upload_control = ipyleaflet.WidgetControl(widget=self.hbox, position="topright")
        self.add_control(upload_control)

    def on_toggle_change(self, change):
        """Toggle visibility of dropdown"""
        if change["new"]:
            self.hbox.children = (self.button, self.file_upload, self.close_button)
        else:
            self.hbox.children = self.close_button

    def on_button_clicked(self, change):
        """Handles the file upload."""
        import io

        if self.file_upload.value:
            # For the first file (if multiple=False)
            file_info = self.file_upload.value[0]
            content_bytes = file_info["content"].tobytes()
            points = pd.read_csv(io.BytesIO(content_bytes))
            self.add_points(points)

    def add_widgets(self):
        """Creates and displays widgets for user interaction."""

        from ipywidgets import jslink
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

        self.add(opacity_control)
        # self.add(date_control)

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

    def change_basemap(self, **kwargs):
        """Changes the basemap of the map using a dropdown selector."""
        from ipywidgets import Dropdown, ToggleButton, HBox, Layout
        from ipyleaflet import WidgetControl, basemap_to_tiles, basemaps

        # Map dropdown names to actual basemap objects
        BASEMAP_LOOKUP = {
            "OpenStreetMap": basemaps.OpenStreetMap.Mapnik,
            "OpenTopoMap": basemaps.OpenTopoMap,
            "Esri.WorldImagery": basemaps.Esri.WorldImagery,
            "CartoDB.DarkMatter": basemaps.CartoDB.DarkMatter,
            "CartoDB.Positron": basemaps.CartoDB.Positron,
            "CartoDB.PositronNoLabels": basemaps.CartoDB.PositronNoLabels,
            "Esri.WorldTopoMap": basemaps.Esri.WorldTopoMap,
            "Esri.WorldStreetMap": basemaps.Esri.WorldStreetMap,
            "Esri.OceanBasemap": basemaps.Esri.OceanBasemap,
            "Esri.NatGeoWorldMap": basemaps.Esri.NatGeoWorldMap,
            "NASAGIBS.ModisTerraTrueColorCR": basemaps.NASAGIBS.ModisTerraTrueColorCR,
            "NASAGIBS.ModisAquaTrueColorCR": basemaps.NASAGIBS.ModisAquaTrueColorCR,
            "NASAGIBS.ViirsTrueColorCR": basemaps.NASAGIBS.ViirsTrueColorCR,
            "NASAGIBS.ViirsEarthAtNight2012": basemaps.NASAGIBS.ViirsEarthAtNight2012,
        }

        # Create widgets
        toggle = ToggleButton(
            value=True,
            tooltip="Toggle basemap selector",
            icon="map",
            layout=Layout(width="38px", height="38px"),
        )

        dropdown = Dropdown(
            options=list(BASEMAP_LOOKUP.keys()),
            value="OpenStreetMap",
            description="Basemap:",
            style={"description_width": "initial"},
            layout=Layout(width="250px", height="38px"),
        )

        # Store reference to current basemap layer
        if not hasattr(self, "current_basemap"):
            self.current_basemap = self.layers[0]

        def on_dropdown_change(change):
            """Handle basemap selection changes"""
            if change["new"]:
                new_basemap = basemap_to_tiles(BASEMAP_LOOKUP[change["new"]])
                self.substitute_layer(self.current_basemap, new_basemap)
                self.current_basemap = new_basemap

        # def on_toggle_change(change):
        #     """Toggle visibility of dropdown"""
        #     if change["new"]:
        #         dropdown.layout.visibility = 'visible'  # Show dropdown
        #     else:
        #         dropdown.layout.visibility = 'hidden'   # Hide dropdown

        # Set up event handlers
        dropdown.observe(on_dropdown_change, names="value")

        # Assemble and add control
        widget_box = HBox([toggle, dropdown])

        is_open = [True]

        def on_toggle_change(change):
            """Toggle visibility of dropdown"""
            if is_open[0] and change["new"]:
                widget_box.children = (toggle, dropdown)
            else:
                widget_box.children = (toggle,)

        toggle.observe(on_toggle_change, names="value")

        control = WidgetControl(widget=widget_box, position="topright")
        self.add_control(control)

    # Using geemap, ipyleaflet, and ipywidgets create a map with a dropdown menu that has any Google Earth Engine dataset

    def add_search_marker(self, **kwargs):
        """Adds a search marker to the map."""

        from ipyleaflet import Map, SearchControl, Marker, AwesomeIcon

        search_marker = Marker(
            icon=AwesomeIcon(name="search", marker_color="blue", icon_color="white")
        )

        search_control = SearchControl(
            position="topleft",
            url="https://nominatim.openstreetmap.org/search?format=json&q={s}",
            zoom=10,
            marker=search_marker,
        )

        self.add(search_control)
