# skiba


[![image](https://img.shields.io/pypi/v/skiba.svg)](https://pypi.python.org/pypi/skiba)
[![image](https://img.shields.io/conda/vn/conda-forge/skiba.svg)](https://anaconda.org/conda-forge/skiba)


### A python package for foresters to query Google Earth Engine data
**Streamlining the process to bring remotely sensed data to foresters**


-   Free software: MIT License
-   Documentation: https://skibapython.streamlit.app/


[![ForestSPOT](docs/files/logo.png)](https://github.com/taraskiba/skiba)


## Walkthrough and Demonstration

[![](https://markdown-videos-api.jorgenkh.no/youtube/eaoYLEwzeQc?si=qXwAPfExQKgODc24)](https://youtu.be/eaoYLEwzeQc?si=qXwAPfExQKgODc24)


## Features

-   Create a map with provided coordinates
-   Access and retrieve band values from Google Earth Engine for provided coordinates or GeoJSON files.
    -   Hide locations of confidential coordinates within a buffered radius.
-   Further developments to come!
-   Please understand the limitations of Google's confidentiality policy before use.

## Installation
```bash
pip install skiba
```

## Quick Start

### 1. Set up Earth Engine
```python
import ee
# First time only - authenticate with Google Earth Engine
ee.Authenticate()
# Initialize with your project
ee.Initialize(project="your-project-id")
```

### 2. Extract NDVI for forest monitoring points
```python
import pandas as pd
from datetime import datetime
from skiba.point_extraction import point_extraction

# Define your forest monitoring locations
forest_points = pd.DataFrame({
    'plot_ID': ['PLOT_001', 'PLOT_002', 'PLOT_003'],
    'LAT': [35.9606, 36.0544, 35.8235],
    'LON': [-83.9207, -112.1401, -84.2875]
})

# Initialize and extract data
pe = point_extraction()
results = pe.get_coordinate_data(
    data=forest_points,
    geedata="COPERNICUS/S2_SR_HARMONIZED",  # Sentinel-2
    start_date=datetime(2024, 6, 1),
    end_date=datetime(2024, 8, 31)
)

# Analyze forest health
print(f"Mean NDVI: {results['NDVI'].mean():.3f}")
```

### 3. Protect sensitive locations with buffering
```python
from skiba.buffer_coordinates import buffer_coordinates

# Create buffers around sensitive plots
bc = buffer_coordinates()
# Set buffer radius (in feet)
bc.buffer_radius.value = 500  # 500 feet buffer

# Process locations while maintaining privacy
# Original coordinates are obscured within buffer radius
```

See the [examples/](examples/) directory for more detailed usage examples

### Logo Credit
-   Logo was designed by HiDream-I1-Dev (https://huggingface.co/spaces/HiDream-ai/HiDream-I1-Dev)