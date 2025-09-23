# Troubleshooting Guide for Skiba

This guide helps you resolve common issues when using skiba for forest monitoring and Earth Engine data extraction.

## Table of Contents
- [Installation Issues](#installation-issues)
- [Earth Engine Authentication](#earth-engine-authentication)
- [Data Extraction Problems](#data-extraction-problems)
- [Performance Issues](#performance-issues)
- [Widget and Display Issues](#widget-and-display-issues)
- [Common Error Messages](#common-error-messages)

## Installation Issues

### Problem: Installation fails with dependency errors
```
ERROR: Could not find a version that satisfies the requirement geemap
```

**Solution:**
```bash
# Upgrade pip first
pip install --upgrade pip

# Install with all dependencies
pip install skiba --upgrade

# Or install dependencies separately
pip install earthengine-api geemap geopandas
pip install skiba
```

### Problem: Import errors after installation
```python
ImportError: cannot import name 'point_extraction' from 'skiba'
```

**Solution:**
```bash
# Reinstall skiba
pip uninstall skiba
pip install skiba --no-cache-dir

# Verify installation
python -c "import skiba; print(skiba.__version__)"
```

## Earth Engine Authentication

### Problem: Authentication fails or expires
```
EEException: Please authenticate to Earth Engine
```

**Solution:**
```python
import ee

# Method 1: Interactive authentication (recommended)
ee.Authenticate()

# Method 2: Service account (for production)
# Create service account at https://console.cloud.google.com/
credentials = ee.ServiceAccountCredentials(
    'your-service-account@project.iam.gserviceaccount.com',
    'path/to/private-key.json'
)
ee.Initialize(credentials=credentials)

# Method 3: Using gcloud (if installed)
ee.Authenticate(auth_mode='gcloud')
```

### Problem: Project ID not set
```
EEException: Project ID is required
```

**Solution:**
```python
# Initialize with your project ID
ee.Initialize(project='your-project-id')

# To find your project ID:
# 1. Go to https://console.cloud.google.com/
# 2. Select your project
# 3. Copy the project ID (not the name)
```

## Data Extraction Problems

### Problem: No data returned from extraction
```python
results = pe.get_coordinate_data(...)
# results is empty or None
```

**Solutions:**

1. **Check date range and cloud coverage:**
```python
# Use longer date range for cloudy regions
start_date = datetime(2024, 1, 1)   # Full year
end_date = datetime(2024, 12, 31)

# For Sentinel-2, filter by cloud coverage
dataset = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
    .filterDate(start_date, end_date) \
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
```

2. **Verify coordinates are correct:**
```python
# Check coordinate order (latitude, longitude)
points = pd.DataFrame({
    'LAT': [45.5231],  # Latitude first (Y)
    'LON': [-122.6765]  # Longitude second (X)
})

# Verify coordinates are in valid range
assert -90 <= points['LAT'].all() <= 90
assert -180 <= points['LON'].all() <= 180
```

3. **Check dataset availability:**
```python
# Verify dataset exists and covers your area
# Check Earth Engine Data Catalog:
# https://developers.google.com/earth-engine/datasets/

# Test with a known working dataset
test_dataset = 'COPERNICUS/S2_SR_HARMONIZED'
```

### Problem: Incorrect band names or indices
```
KeyError: 'NDVI'
```

**Solution:**
```python
# Check available bands first
print(results.columns.tolist())

# Calculate NDVI manually if not provided
if 'B4' in results.columns and 'B5' in results.columns:
    # For Landsat
    results['NDVI'] = (results['B5'] - results['B4']) / (results['B5'] + results['B4'])
elif 'B8' in results.columns and 'B4' in results.columns:
    # For Sentinel-2
    results['NDVI'] = (results['B8'] - results['B4']) / (results['B8'] + results['B4'])
```

### Problem: CSV column names not recognized
```
ValueError: No matching column found for ['lat', 'latitude', ...]
```

**Solution:**
```python
# Ensure your CSV has the correct column names
# Accepted latitude columns: lat, latitude, y, LAT, Latitude, Lat, Y
# Accepted longitude columns: lon, long, longitude, x, LON, Longitude, Long, X
# Accepted ID columns: id, ID, plot_ID, plot_id, plotID, plotId

# Rename columns if needed
df = pd.read_csv('your_file.csv')
df = df.rename(columns={
    'your_lat_column': 'LAT',
    'your_lon_column': 'LON',
    'your_id_column': 'plot_ID'
})
```

## Performance Issues

### Problem: Extraction takes too long
**Solutions:**

1. **Reduce spatial extent:**
```python
# Process in smaller batches
batch_size = 100
for i in range(0, len(points), batch_size):
    batch = points[i:i+batch_size]
    results = pe.get_coordinate_data(batch, ...)
```

2. **Use coarser resolution:**
```python
# Use MODIS instead of Sentinel-2 for large areas
dataset = 'MODIS/006/MOD13Q1'  # 250m resolution vs 10m
```

3. **Reduce temporal range:**
```python
# Extract monthly instead of daily
# Process one month at a time
```

### Problem: Memory errors with large datasets
```
MemoryError: Unable to allocate array
```

**Solution:**
```python
# Process data in chunks
chunk_size = 1000
chunks = []
for chunk in pd.read_csv('large_file.csv', chunksize=chunk_size):
    result = pe.get_coordinate_data(chunk, ...)
    chunks.append(result)

final_results = pd.concat(chunks, ignore_index=True)
```

## Widget and Display Issues

### Problem: Widgets not displaying in Jupyter
**Solution:**
```bash
# Install and enable widget extensions
pip install ipywidgets
jupyter nbextension enable --py widgetsnbextension

# For JupyterLab
jupyter labextension install @jupyter-widgets/jupyterlab-manager
```

### Problem: Map not displaying
**Solution:**
```python
# Use appropriate map library
import folium
import ipyleaflet

# Check if running in Jupyter
try:
    get_ipython()
    # Use ipyleaflet for Jupyter
    from skiba.ipyleafletcode import create_map
except:
    # Use folium for scripts
    from skiba.foliumcode import create_map
```

## Common Error Messages

### `EEException: User memory limit exceeded`
**Cause:** Requesting too much data at once.
**Fix:** Reduce area, time range, or use `.select()` to get only needed bands.

### `HttpError 429: Quota exceeded`
**Cause:** Too many requests to Earth Engine.
**Fix:** Add delays between requests or upgrade Earth Engine quota.

### `AttributeError: 'NoneType' object has no attribute 'getInfo'`
**Cause:** Earth Engine not initialized or asset doesn't exist.
**Fix:** Ensure `ee.Initialize()` is called and check asset path.

### `ValueError: Cannot convert to GeoDataFrame`
**Cause:** Invalid geometry or coordinate data.
**Fix:** Check coordinate format and ensure valid geometries.

## Getting Help

If you're still experiencing issues:

1. **Check the examples:**
   - See the [examples/](examples/) directory for working code
   - Run examples to verify your setup

2. **Enable debug logging:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

3. **Report issues:**
   - GitHub Issues: https://github.com/taraskiba/skiba/issues
   - Include: Error message, code snippet, package versions

4. **Package versions:**
```python
import skiba, ee, geemap, geopandas
print(f"skiba: {skiba.__version__}")
print(f"earthengine-api: {ee.__version__}")
print(f"geemap: {geemap.__version__}")
print(f"geopandas: {geopandas.__version__}")
```

## Best Practices

1. **Always test with small datasets first**
2. **Use try-except blocks for Earth Engine calls**
3. **Save intermediate results to avoid re-processing**
4. **Monitor Earth Engine quotas in Cloud Console**
5. **Use appropriate datasets for your scale of analysis**