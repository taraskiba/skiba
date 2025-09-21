#!/usr/bin/env python
"""
Basic Point Extraction Example
==============================

This example demonstrates how to extract Earth Engine data for specific forest monitoring points.
Perfect for foresters who need to monitor vegetation indices at specific locations.
"""

import pandas as pd
from datetime import datetime
import ee
from skiba.point_extraction import point_extraction

# Initialize Earth Engine (you need to authenticate first time)
# ee.Authenticate()
ee.Initialize(project="your-project-id")  # Replace with your GEE project ID


def extract_ndvi_for_forest_points():
    """
    Extract NDVI values for forest monitoring points.

    This example shows how to:
    1. Define forest monitoring locations
    2. Extract NDVI values from Sentinel-2
    3. Analyze the results
    """

    # Define forest monitoring points
    # These could be plot centers, phenocam locations, or flux tower sites
    forest_points = pd.DataFrame(
        {
            "plot_ID": ["PLOT_001", "PLOT_002", "PLOT_003", "PLOT_004"],
            "LAT": [35.9606, 36.0544, 35.8235, 36.1069],
            "LON": [-83.9207, -112.1401, -84.2875, -112.0693],
            "forest_type": ["Mixed Deciduous", "Coniferous", "Oak-Hickory", "Pine"],
        }
    )

    # Save to CSV for use with point_extraction
    forest_points.to_csv("forest_monitoring_points.csv", index=False)

    # Initialize point extraction
    pe = point_extraction()

    # Set parameters
    start_date = datetime(2024, 6, 1)  # Summer season
    end_date = datetime(2024, 8, 31)

    # Use Sentinel-2 Surface Reflectance
    dataset = "COPERNICUS/S2_SR_HARMONIZED"

    # Extract data
    print("Extracting NDVI values for forest monitoring points...")
    results = pe.get_coordinate_data(
        data="forest_monitoring_points.csv",
        geedata=dataset,
        start_date=start_date,
        end_date=end_date,
    )

    # Analyze results
    print("\n=== Forest Health Analysis ===")
    print(f"Data extracted for {len(results)} points")

    if "NDVI" in results.columns:
        print(f"\nNDVI Statistics:")
        print(f"Mean NDVI: {results['NDVI'].mean():.3f}")
        print(f"Min NDVI: {results['NDVI'].min():.3f}")
        print(f"Max NDVI: {results['NDVI'].max():.3f}")

        # Identify potential problem areas
        low_ndvi_threshold = 0.4
        problem_plots = results[results["NDVI"] < low_ndvi_threshold]
        if not problem_plots.empty:
            print(f"\n⚠️ Plots with low NDVI (< {low_ndvi_threshold}):")
            for _, plot in problem_plots.iterrows():
                print(f"  - {plot['plot_ID']}: NDVI = {plot['NDVI']:.3f}")

    return results


def extract_multiple_indices():
    """
    Extract multiple vegetation indices for comprehensive forest health assessment.
    """

    print("\n=== Extracting Multiple Vegetation Indices ===")

    # Sample coordinates for a forest stand
    forest_stand = pd.DataFrame(
        {
            "plot_ID": ["STAND_A1", "STAND_A2", "STAND_A3"],
            "LAT": [45.5231, 45.5245, 45.5259],
            "LON": [-122.6765, -122.6750, -122.6735],
        }
    )

    pe = point_extraction()

    # Extract from Landsat 8 for longer time series
    dataset = "LANDSAT/LC08/C02/T1_L2"
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31)

    results = pe.get_coordinate_data(
        data=forest_stand, geedata=dataset, start_date=start_date, end_date=end_date
    )

    print(f"Extracted data shape: {results.shape}")
    print(f"Available bands: {results.columns.tolist()}")

    # Calculate additional indices if bands are available
    if "B5" in results.columns and "B4" in results.columns:  # NIR and Red
        results["NDVI"] = (results["B5"] - results["B4"]) / (
            results["B5"] + results["B4"]
        )
        print(
            f"Calculated NDVI range: {results['NDVI'].min():.3f} to {results['NDVI'].max():.3f}"
        )

    if "B5" in results.columns and "B3" in results.columns:  # NIR and Green
        results["GNDVI"] = (results["B5"] - results["B3"]) / (
            results["B5"] + results["B3"]
        )
        print(
            f"Calculated GNDVI range: {results['GNDVI'].min():.3f} to {results['GNDVI'].max():.3f}"
        )

    return results


def main():
    """Run all examples."""

    print("=" * 60)
    print("SKIBA - Forest Monitoring Point Extraction Examples")
    print("=" * 60)

    try:
        # Example 1: Basic NDVI extraction
        ndvi_results = extract_ndvi_for_forest_points()

        # Example 2: Multiple indices extraction
        multi_index_results = extract_multiple_indices()

        print("\n✅ Examples completed successfully!")
        print("Check the generated CSV files for full results.")

    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        print("Make sure you have:")
        print("1. Authenticated with Earth Engine (ee.Authenticate())")
        print("2. Set up your GEE project ID")
        print("3. Installed all required dependencies")


if __name__ == "__main__":
    main()
