# skiba


[![image](https://img.shields.io/pypi/v/skiba.svg)](https://pypi.python.org/pypi/skiba)
[![image](https://img.shields.io/conda/vn/conda-forge/skiba.svg)](https://anaconda.org/conda-forge/skiba)


### A python package for foresters to query Google Earth Engine data
**Streamlining the process to bring remotely sensed data to foresters**

[![ForestSPOT](docs/files/logo.png)](https://github.com/taraskiba/skiba)


-   Free software: MIT License
-   Documentation: https://taraskiba.github.io/skiba/


## Walkthrough and Demonstration

[![](https://markdown-videos-api.jorgenkh.no/youtube/eaoYLEwzeQc?si=qXwAPfExQKgODc24)](https://youtu.be/eaoYLEwzeQc?si=qXwAPfExQKgODc24)


## Features

-   Access and retrieve pixel values from Google Earth Engine Images or ImageCollections and a desired time-period for a .CSV provided coordinates.
    -   Results can be exported averaged over matching plot IDs or individual points.
-   Buffer sensitive coordinates:
    -   Buffer to a singular point within a specified radius.
    -   Buffer to *n* points within a specified radius.
-   Create a map with provided coordinates and built-in basemaps and geojson overlays.
-   Please understand the limitations of Google's confidentiality policy before use.

## Installation
```python
pip install skiba
```

Once installed, you need to authenticate your Google Earth Engine account. You can do this by running the following commands in Python:

```python
import ee
# Initialize Earth Engine
ee.Authenticate()
ee.Initialize(project="ee-forestplotvariables")
```

To load widget boxes, run the following command in Python:

```python
# For single point buffering
import skiba.buffer_coordinates as sbc
single = sbc.buffer_coordinates().vbox
single

# For multiple point buffering
import skiba.buffer_and_sample as sbs
multiple = sbs.buffer().vbox
multiple

# For non-aggregated point extraction
import skiba.point_extraction as spe
point = spe.point_extraction().vbox
point

# For aggregated point extraction


# For the mapping tool
import skiba.interactive as map
m = map.Map()
m
```

## Web App

For a non-python user, you can access the Streamlit app here:
https://gskiba.streamlit.app/

### Logo Credit

-   Logo was designed by HiDream-I1-Dev (https://huggingface.co/spaces/HiDream-ai/HiDream-I1-Dev)