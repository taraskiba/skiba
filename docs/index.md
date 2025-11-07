# Welcome to skiba


[![image](https://img.shields.io/pypi/v/skiba.svg)](https://pypi.python.org/pypi/skiba)


**A python package for a foresters to query Google Earth Engine data**


-   Free software: MIT License
-   Documentation: <https://taraskiba.github.io/skiba>
-   Streamlit App: <https://gskiba.streamlit.app/>

[![ForestSPOT](./files/logo.png)](https://github.com/taraskiba/skiba/tree/main/docs/files/logo.png)
## Features

-   Access and retrieve pixel values from Google Earth Engine Images or ImageCollections and a desired time-period for a .CSV provided coordinates.
    -   Results can be exported averaged over matching plot IDs or individual points.
-   Buffer sensitive coordinates:
    -   Buffer to a singular point within a specified radius.
    -   Buffer to *n* points within a specified radius.
-   Create a map with provided coordinates and built-in basemaps and geojson overlays.
-   Please understand the limitations of Google's confidentiality policy before use.