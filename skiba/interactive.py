import ipyleaflet
import ipywidgets as widgets
import geopandas as gpd
import pandas as pd
import geemap as gm

# import os

# This code adds various widgets to the map for user interaction.


class Map(ipyleaflet.Map):
    def __init__(self, center=[37.5, -95], zoom=4, height="600px", **kwargs):
        """Initialize the map with a given center and zoom level.

        Args:
            center (list, optional): Center coordinates of the map. Defaults to [37.5, -95].
            zoom (int, optional): Zoom level of the map. Defaults to 4.
            height (str, optional): Height of the map. Defaults to "600px".
            **kwargs: Additional keyword arguments for ipyleaflet.Map.
        """
        super().__init__(center=center, zoom=zoom, **kwargs)
        self.layout.height = height
        self.scroll_wheel_zoom = True
        self.add_layer_control()
        self.change_basemap()
        self.add_search_marker()
        self.upload_points()
        self.upload_geojson_file()
        self.change_built_in_shapefiles()
        self.on_interaction(self.handle_click)
        self.geojson_button()

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

    def handle_click(self, **kwargs):
        """Handles click events on the map."""
        if kwargs.get("type") == "click":
            self.add_layer(ipyleaflet.Marker(location=kwargs.get("coordinates")))

            print(f"Clicked at: {kwargs.get('coordinates')}")

    def add_layer_control(self):
        """Adds a layer control widget to the map."""
        control = ipyleaflet.LayersControl(position="topright")
        self.add_control(control)

    def add_geojson(self, data, hover_style=None, **kwargs):
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

        if (
            hasattr(self, "current_geojson_layer")
            and self.current_geojson_layer is not None
        ):
            try:
                self.remove_layer(self.current_geojson_layer)
            except Exception:
                pass  # Layer might have already been removed

        layer = ipyleaflet.GeoJSON(
            data=geojson, hover_style=hover_style, style=style, **kwargs
        )
        self.current_geojson_layer = layer
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
            "radius": 2,
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

        button = Button(
            description="Add Points",
            disabled=False,
            button_style="",  # 'success', 'info', 'warning', 'danger' or ''
            tooltip="Click me",
            size=38,
            icon="plus",  # (FontAwesome names without the `fa-` prefix)
        )

        file_upload = FileUpload(
            accept=".csv",
            multiple=False,
            size=38,
            description="Upload CSV",
            style={"description_width": "initial"},
        )

        close_button = ToggleButton(
            icon="map-pin", value=True, tooltip="Upload points from CSV file"
        )
        close_button.layout = widgets.Layout(width="36px", height="36px")

        hbox = HBox([close_button])

        is_open = [True]

        def on_toggle_change(change):
            """Toggle visibility of dropdown"""
            if is_open[0] and change["new"]:
                hbox.children = (close_button,)
            else:
                hbox.children = (close_button, file_upload, button)

        def on_button_clicked(change):
            """Handles the file upload."""
            import io

            if file_upload.value:
                # For the first file (if multiple=False)
                file_info = file_upload.value[0]
                content_bytes = file_info["content"].tobytes()
                points = pd.read_csv(io.BytesIO(content_bytes))
                self.add_points(points)

        close_button.observe(on_toggle_change, names="value")

        button.on_click(on_button_clicked)

        upload_control = ipyleaflet.WidgetControl(widget=hbox, position="topright")
        self.add_control(upload_control)

    def upload_geojson_file(self, **kwargs):
        """Uploads GeoJSON file to the map."""

        from ipywidgets import FileUpload, Button, ToggleButton, HBox

        button = Button(
            description="Add GeoJSON file",
            disabled=False,
            button_style="",  # 'success', 'info', 'warning', 'danger' or ''
            tooltip="Click me",
            size=38,
            icon="plus",  # (FontAwesome names without the `fa-` prefix)
        )

        file_upload = FileUpload(
            accept=".geojson",
            multiple=False,
            size=38,
            description="Upload GeoJSON",
            style={"description_width": "initial"},
        )

        close_button = ToggleButton(icon="file", value=True, tooltip="Add GeoJSON file")
        close_button.layout = widgets.Layout(width="36px", height="36px")

        hbox = HBox([close_button])

        is_open = [True]

        def on_toggle_change(change):
            """Toggle visibility of dropdown"""
            if change["new"]:
                hbox.children = (close_button,)
            else:
                hbox.children = (close_button, file_upload, button)

        def on_button_clicked(change):
            """Handles the url upload."""
            if file_upload.value and len(file_upload.value) > 0:
                import json
                from ipyleaflet import GeoJSON

                file_info = file_upload.value[0]
                # Get bytes from memoryview
                content_bytes = file_info["content"].tobytes()
                # Decode bytes to string, then load as JSON
                geojson_data = json.loads(content_bytes.decode("utf-8"))
                # Add the GeoJSON layer to the map
                geo_json = GeoJSON(data=geojson_data)
                self.add_layer(geo_json)

        close_button.observe(on_toggle_change, names="value")

        button.on_click(on_button_clicked)

        upload_control = ipyleaflet.WidgetControl(widget=hbox, position="topright")
        self.add_control(upload_control)

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
            tooltip="Change basemap",
            icon="map-o",
            layout=Layout(width="36px", height="36px"),
        )

        dropdown = Dropdown(
            options=list(BASEMAP_LOOKUP.keys()),
            value="OpenStreetMap",
            description="Basemap:",
            style={"description_width": "initial"},
            layout=Layout(width="250px", height="36px"),
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
        widget_box = HBox([toggle])

        is_open = [True]

        def on_toggle_change(change):
            """Toggle visibility of dropdown"""
            if is_open[0] and change["new"]:
                widget_box.children = (toggle,)
            else:
                widget_box.children = (toggle, dropdown)

        toggle.observe(on_toggle_change, names="value")

        control = WidgetControl(widget=widget_box, position="topright")
        self.add_control(control)

    def change_built_in_shapefiles(self, **kwargs):
        """Changes the basemap of the map using a dropdown selector."""
        from ipywidgets import Dropdown, ToggleButton, HBox, Layout
        from ipyleaflet import WidgetControl

        # Map dropdown names to actual basemap objects
        SHAPEFILE_LOOKUP = {
            "None": None,
            "U.S. States": "../data/us-states.json",
            "National Forests": "https://geohub.oregon.gov/api/download/v1/items/b479e4bd7d70439a87e0230c99bddce5/geojson?layers=0",
        }

        # Create widgets
        toggle = ToggleButton(
            value=True,
            tooltip="Add built-in shapefile",
            icon="square-o",
            layout=Layout(width="38px", height="38px"),
        )

        dropdown = Dropdown(
            options=list(SHAPEFILE_LOOKUP.keys()),
            value="None",
            placeholder="Select a shapefile",
            description="Select shapefile:",
            style={"description_width": "initial"},
            layout=Layout(width="250px", height="38px"),
        )

        # Store reference to current basemap layer
        if not hasattr(self, "current_basemap"):
            self.current_basemap = self.layers[0]

        def on_dropdown_change(change):
            """Handle shapefile selection changes"""
            if change["new"]:
                geojson_path = SHAPEFILE_LOOKUP[change["new"]]
                if geojson_path is not None:
                    self.add_geojson(geojson_path, name=change["new"])
                else:
                    # Remove existing shapefile layer if "None" is selected
                    if (
                        hasattr(self, "current_geojson_layer")
                        and self.current_geojson_layer is not None
                    ):
                        try:
                            self.remove_layer(self.current_geojson_layer)
                        except Exception:
                            pass

        # Set up event handlers
        dropdown.observe(on_dropdown_change, names="value")

        # Assemble and add control
        widget_box = HBox([toggle])

        is_open = [True]

        def on_toggle_change(change):
            """Toggle visibility of dropdown"""
            if is_open[0] and change["new"]:
                widget_box.children = (toggle,)
            else:
                widget_box.children = (toggle, dropdown)

        toggle.observe(on_toggle_change, names="value")

        control = WidgetControl(widget=widget_box, position="topright")
        self.add_control(control)

    def add_search_marker(self, **kwargs):
        """Adds a search marker to the map."""

        from ipyleaflet import SearchControl, Marker, AwesomeIcon

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

    def geojson_button(self, **kwargs):
        """Creates a button to add shapefiles."""
        from ipywidgets import Button, Text, ToggleButton, HBox, Layout
        from ipyleaflet import WidgetControl

        # Create widgets
        toggle_close = ToggleButton(
            value=True, tooltip="Add GeoJSON from link", icon="link"
        )

        url = Text(
            placeholder="Type something",
            description="GeoJSON URL:",
            disabled=False,
            style={"description_width": "initial"},
        )

        run_button = Button(
            description="Add GeoJSON",
            disabled=False,
            button_style="",  # 'success', 'info', 'warning', 'danger' or ''
            tooltip="Click me",
            size=38,
            icon="plus",  # (FontAwesome names without the `fa-` prefix)
        )

        toggle_close.layout = Layout(width="36px", height="36px")

        # Assemble and add control
        widget_box = HBox([toggle_close])

        def on_toggle_change(change):
            """Toggle visibility of dropdown"""
            if change["new"]:
                widget_box.children = (toggle_close,)
            else:
                widget_box.children = (toggle_close, url, run_button)

        def on_button_clicked(change):
            """Handles the url upload."""
            if url.value:
                # For the first file (if multiple=False)
                geojson_path = url.value
                self.add_geojson(geojson_path, name=url.value)

        toggle_close.observe(on_toggle_change, names="value")

        run_button.on_click(on_button_clicked)

        control = WidgetControl(widget=widget_box, position="topright")

        self.add_control(control)
