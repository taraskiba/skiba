# Skiba Examples

This directory contains practical examples demonstrating how to use skiba for forest monitoring and Earth Engine data extraction.

## Quick Start

Before running any examples, make sure you have:
1. Installed skiba: `pip install skiba`
2. Authenticated with Google Earth Engine: `earthengine authenticate`
3. Set up a Google Earth Engine project

## Examples Overview

### 01. Basic Point Extraction (`01_basic_point_extraction.py`)
Learn how to:
- Extract vegetation indices (NDVI) for specific forest monitoring points
- Process data from Sentinel-2 and Landsat satellites
- Analyze forest health metrics
- Handle multiple vegetation indices (NDVI, GNDVI, EVI)

**Use cases:**
- Forest plot monitoring
- Phenology tracking at specific locations
- Flux tower or phenocam site analysis

### 02. Buffer and Privacy Protection (`02_buffer_and_privacy.py`)
Learn how to:
- Create buffers around sensitive plot locations
- Generate random sample points within buffers
- Maintain location privacy while extracting data
- Implement different buffer sizes based on sensitivity levels

**Use cases:**
- Protecting endangered species locations
- Confidential research plot management
- Privacy-compliant data sharing

### 03. Area-Based Extraction (`03_area_extraction.py`)
Learn how to:
- Extract data for entire forest management units
- Calculate watershed-level statistics
- Compare multiple forest parcels
- Rank areas for different management objectives

**Use cases:**
- Forest stand health assessment
- Watershed forest monitoring
- Timber harvest planning
- Conservation prioritization

## Running the Examples

### Basic Usage

```bash
# Run a specific example
python examples/01_basic_point_extraction.py

# Or import in your own script
from examples.basic_point_extraction import extract_ndvi_for_forest_points
results = extract_ndvi_for_forest_points()
```

### Required Setup

1. **Earth Engine Authentication** (first time only):
```python
import ee
ee.Authenticate()
```

2. **Initialize with your project**:
```python
ee.Initialize(project="your-project-id")
```

## Example Data Formats

### Point Data (CSV)
```csv
plot_ID,LAT,LON
PLOT_001,35.9606,-83.9207
PLOT_002,36.0544,-112.1401
```

### GeoJSON Features
```json
{
  "type": "FeatureCollection",
  "features": [{
    "type": "Feature",
    "properties": {"stand_id": "STAND_001"},
    "geometry": {
      "type": "Polygon",
      "coordinates": [[[-122.5, 45.5], ...]]
    }
  }]
}
```

## Common Datasets

### Optical Satellites
- **Sentinel-2**: `COPERNICUS/S2_SR_HARMONIZED`
  - 10m resolution, 5-day revisit
  - Best for detailed vegetation monitoring

- **Landsat 8**: `LANDSAT/LC08/C02/T1_L2`
  - 30m resolution, 16-day revisit
  - Good for long-term time series

- **MODIS**: `MODIS/006/MOD13Q1`
  - 250m resolution, daily
  - Best for large-scale monitoring

### Vegetation Indices
- **NDVI**: Normalized Difference Vegetation Index
  - Formula: `(NIR - Red) / (NIR + Red)`
  - Range: -1 to 1 (healthy vegetation: 0.6-0.9)

- **EVI**: Enhanced Vegetation Index
  - Better for dense canopy
  - Less sensitive to atmospheric conditions

## Troubleshooting

### Common Issues

1. **Authentication Error**
   ```
   Error: Please authorize access to Earth Engine
   Solution: Run ee.Authenticate() and follow the prompts
   ```

2. **No Data Returned**
   - Check date range (cloud cover can limit data)
   - Verify coordinates are correct
   - Ensure dataset is available for your region

3. **Memory Errors**
   - Reduce the size of your study area
   - Use fewer dates or coarser resolution
   - Process data in smaller chunks

## Advanced Usage

### Custom Band Calculations
```python
# Calculate custom indices from band values
results['NDWI'] = (results['B3'] - results['B5']) / (results['B3'] + results['B5'])
results['SAVI'] = ((results['B5'] - results['B4']) / (results['B5'] + results['B4'] + 0.5)) * 1.5
```

### Time Series Analysis
```python
# Extract monthly averages
for month in range(1, 13):
    start = datetime(2024, month, 1)
    end = datetime(2024, month, 28)
    monthly_data = pe.get_coordinate_data(data, dataset, start, end)
    # Process monthly data
```

### Batch Processing
```python
# Process multiple datasets
datasets = [
    "COPERNICUS/S2_SR_HARMONIZED",
    "LANDSAT/LC08/C02/T1_L2",
    "MODIS/006/MOD13Q1"
]

all_results = {}
for dataset in datasets:
    all_results[dataset] = pe.get_coordinate_data(data, dataset, start_date, end_date)
```

## Contributing

Have a useful example? Please contribute! See the main [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

## Support

For issues or questions:
- Check the [FAQ](../docs/faq.md)
- Open an issue on [GitHub](https://github.com/taraskiba/skiba/issues)
- See the full [documentation](https://skibapython.streamlit.app/)