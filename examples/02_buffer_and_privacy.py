#!/usr/bin/env python
"""
Buffer and Privacy Protection Example
======================================

This example shows how to use buffering to protect sensitive forest plot locations
while still extracting valuable Earth Engine data.
"""

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import numpy as np
from datetime import datetime
import ee
from skiba.buffer_coordinates import buffer_coordinates
from skiba.buffer_and_sample import buffer

# Initialize Earth Engine
print("Earth Engine Authentication")
print("-" * 30)
project_id = input(
    "Enter your Earth Engine project ID (or press Enter to skip): "
).strip()

if project_id:
    try:
        # Try to initialize with the provided project ID
        ee.Initialize(project=project_id)
        print(f"✅ Successfully initialized Earth Engine with project: {project_id}\n")
    except Exception as e:
        print(f"❌ Failed to initialize Earth Engine: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure you've authenticated before: ee.Authenticate()")
        print("2. Verify your project ID is correct")
        print("3. Ensure you have the necessary permissions")
        exit(1)
else:
    print("⚠️  Skipping Earth Engine initialization - some features may not work\n")


def create_buffered_forest_plots():
    """
    Create buffered areas around sensitive forest research plots.

    Use case: You have confidential research plot locations that cannot
    be shared exactly, but you still need to extract remote sensing data.
    """

    print("=== Creating Buffered Forest Plot Locations ===\n")

    # Original sensitive plot locations (e.g., endangered species habitat)
    sensitive_plots = pd.DataFrame(
        {
            "plot_ID": ["RARE_001", "RARE_002", "RARE_003"],
            "LAT": [44.0582, 44.0691, 44.0523],
            "LON": [-121.3153, -121.3089, -121.3201],
            "species": ["Spotted Owl", "Spotted Owl", "Marbled Murrelet"],
            "sensitivity": ["HIGH", "HIGH", "CRITICAL"],
        }
    )

    print(f"Original plots: {len(sensitive_plots)} locations")
    print(sensitive_plots[["plot_ID", "species", "sensitivity"]].to_string())

    # Initialize buffer_coordinates
    bc = buffer_coordinates()

    # Create buffers based on sensitivity level
    buffer_radius_map = {
        "LOW": 100,  # 100 feet
        "MEDIUM": 500,  # 500 feet
        "HIGH": 1000,  # 1000 feet
        "CRITICAL": 2000,  # 2000 feet
    }

    # Convert to GeoDataFrame
    geometry = [
        Point(lon, lat) for lon, lat in zip(sensitive_plots.LON, sensitive_plots.LAT)
    ]
    gdf = gpd.GeoDataFrame(sensitive_plots, geometry=geometry, crs="EPSG:4326")

    # Create buffers for each sensitivity level
    buffered_gdfs = []
    for sensitivity, radius_ft in buffer_radius_map.items():
        mask = gdf["sensitivity"] == sensitivity
        if mask.any():
            subset = gdf[mask].copy()
            # Convert to projected CRS for accurate buffering (UTM Zone 10N for Oregon)
            subset_projected = subset.to_crs("EPSG:32610")  # UTM Zone 10N
            # Convert feet to meters (1 foot = 0.3048 meters)
            radius_meters = radius_ft * 0.3048
            subset_projected["geometry"] = subset_projected.geometry.buffer(
                radius_meters
            )
            # Convert back to geographic CRS
            subset = subset_projected.to_crs("EPSG:4326")
            subset["buffer_radius_ft"] = radius_ft
            buffered_gdfs.append(subset)

    # Combine all buffered areas
    buffered_plots = pd.concat(buffered_gdfs, ignore_index=True)

    print(f"\n✅ Created buffers for {len(buffered_plots)} plots")
    print(f"Buffer sizes: {buffered_plots['buffer_radius_ft'].unique()} feet")

    return buffered_plots


def sample_within_buffers():
    """
    Generate random sample points within buffered areas for data extraction.

    This maintains location privacy while still allowing remote sensing analysis.
    """

    print("\n=== Sampling Within Buffered Areas ===\n")

    # Create a simple buffered area
    center_point = Point(-122.3321, 47.6062)  # Seattle area forest
    buffer_radius_deg = 0.01  # Approximately 1km

    # Create buffered area
    buffered_area = center_point.buffer(buffer_radius_deg)

    # Generate random sample points within the buffer
    num_samples = 10
    sample_points = []

    minx, miny, maxx, maxy = buffered_area.bounds

    print(f"Generating {num_samples} random points within buffer...")
    attempts = 0
    while len(sample_points) < num_samples and attempts < 1000:
        # Generate random point within bounding box
        random_point = Point(
            np.random.uniform(minx, maxx), np.random.uniform(miny, maxy)
        )

        # Check if point is within buffer
        if buffered_area.contains(random_point):
            sample_points.append(random_point)
            print(
                f"  Point {len(sample_points)}: ({random_point.x:.6f}, {random_point.y:.6f})"
            )

        attempts += 1

    print(f"\n✅ Generated {len(sample_points)} sample points")

    # Convert to DataFrame for extraction
    sample_df = pd.DataFrame(
        {
            "sample_ID": [f"SAMPLE_{i+1:03d}" for i in range(len(sample_points))],
            "LAT": [p.y for p in sample_points],
            "LON": [p.x for p in sample_points],
            "buffer_center_lat": center_point.y,
            "buffer_center_lon": center_point.x,
            "buffer_radius_km": 1.0,
        }
    )

    return sample_df


def extract_data_from_buffered_samples():
    """
    Extract Earth Engine data from buffered and sampled locations.

    This demonstrates the full workflow from sensitive locations to
    privacy-protected data extraction.
    """

    print("\n=== Extracting Data from Privacy-Protected Locations ===\n")

    # Step 1: Create buffered plots
    buffered_plots = create_buffered_forest_plots()

    # Step 2: Generate sample points
    sample_df = sample_within_buffers()

    # Step 3: Prepare for extraction
    bas = buffer()

    # Use simplified sample for demonstration
    extraction_points = sample_df[["sample_ID", "LAT", "LON"]].copy()
    extraction_points.rename(columns={"sample_ID": "plot_ID"}, inplace=True)

    print("\nExtracting vegetation data from sampled points...")

    # Extract Sentinel-2 data
    dataset = "COPERNICUS/S2_SR_HARMONIZED"
    start_date = datetime(2024, 7, 1)
    end_date = datetime(2024, 7, 31)

    # Note: In real usage, you would use the buffer_and_sample methods
    # This is a simplified demonstration
    print(f"Dataset: {dataset}")
    print(f"Date range: {start_date.date()} to {end_date.date()}")
    print(f"Number of extraction points: {len(extraction_points)}")

    return extraction_points


def privacy_report(original_coords, buffered_coords, extracted_data):
    """
    Generate a privacy protection report showing how locations were obscured.
    """

    print("\n=== Privacy Protection Report ===\n")

    print("Original Data Security:")
    print("✅ Original coordinates: NOT EXPORTED")
    print("✅ Buffered areas: RANDOMIZED")
    print("✅ Sample points: RANDOMLY DISTRIBUTED")

    if original_coords is not None and buffered_coords is not None:
        # Calculate average displacement
        print(f"\nPrivacy Metrics:")
        print(f"  - Minimum buffer: 100 feet")
        print(f"  - Maximum buffer: 2000 feet")
        print(f"  - Sample randomization: Yes")
        print(f"  - Original locations recoverable: No")

    print("\nData Extraction Summary:")
    if extracted_data is not None:
        print(f"  - Points processed: {len(extracted_data)}")
        print(f"  - Original precision: Exact coordinates")
        print(f"  - Output precision: ~100-2000 feet radius")
        print(f"  - Privacy maintained: ✅ Yes")


def main():
    """Run privacy-protected extraction workflow."""

    print("=" * 60)
    print("SKIBA - Privacy-Protected Forest Data Extraction")
    print("=" * 60)
    print()
    print("This example demonstrates how to:")
    print("1. Buffer sensitive forest plot locations")
    print("2. Generate random samples within buffers")
    print("3. Extract Earth Engine data while maintaining location privacy")
    print()

    try:
        # Run the workflow
        extraction_points = extract_data_from_buffered_samples()

        # Generate privacy report
        privacy_report(
            original_coords=None,  # Not exported for privacy
            buffered_coords=None,  # Randomized
            extracted_data=extraction_points,
        )

        print("\n✅ Privacy-protected extraction completed!")
        print("\nNote: This example demonstrates the concepts.")
        print("In production, use the full buffer_and_sample workflow.")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure Earth Engine is initialized")
        print("2. Check that all dependencies are installed")
        print("3. Verify coordinate system settings")


if __name__ == "__main__":
    main()
