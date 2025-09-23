#!/usr/bin/env python
"""
Area-Based Extraction Example
==============================

Extract Earth Engine data for forest management units, watersheds, or other
polygon features rather than just points.
"""

import json
import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import Polygon, Point
from datetime import datetime
import ee
from skiba.area_extraction import point_extraction

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


def extract_data_for_forest_stands():
    """
    Extract remote sensing data for entire forest management units.

    Use case: Forest managers need average NDVI values for each
    management unit to assess overall forest health.
    """

    print("=== Extracting Data for Forest Management Units ===\n")

    # Create sample forest stand polygons
    # In practice, these would come from your GIS system
    forest_stands = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "stand_id": "STAND_001",
                    "area_ha": 25.5,
                    "forest_type": "Douglas Fir",
                    "age_years": 45,
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [-122.5, 45.5],
                            [-122.48, 45.5],
                            [-122.48, 45.52],
                            [-122.5, 45.52],
                            [-122.5, 45.5],
                        ]
                    ],
                },
            },
            {
                "type": "Feature",
                "properties": {
                    "stand_id": "STAND_002",
                    "area_ha": 18.3,
                    "forest_type": "Mixed Conifer",
                    "age_years": 60,
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [-122.48, 45.5],
                            [-122.46, 45.5],
                            [-122.46, 45.52],
                            [-122.48, 45.52],
                            [-122.48, 45.5],
                        ]
                    ],
                },
            },
        ],
    }

    # Save as GeoJSON for processing
    with open("forest_stands.geojson", "w") as f:
        json.dump(forest_stands, f, indent=2)

    print(f"Created {len(forest_stands['features'])} forest stand polygons")

    # Initialize area extraction
    ae = point_extraction()

    # Extract Sentinel-2 data for summer period
    dataset = "COPERNICUS/S2_SR_HARMONIZED"
    start_date = datetime(2024, 6, 1)
    end_date = datetime(2024, 8, 31)

    print(f"\nExtracting data from: {dataset}")
    print(f"Date range: {start_date.date()} to {end_date.date()}")

    # Process each stand
    results = []
    for feature in forest_stands["features"]:
        stand_id = feature["properties"]["stand_id"]
        print(f"\nProcessing {stand_id}...")

        # In actual implementation, use ae.get_area_data()
        # This is a conceptual demonstration
        result = {
            "stand_id": stand_id,
            "forest_type": feature["properties"]["forest_type"],
            "area_ha": feature["properties"]["area_ha"],
            "mean_ndvi": 0.65
            + (0.1 * (1 if "Fir" in feature["properties"]["forest_type"] else 0)),
            "min_ndvi": 0.45,
            "max_ndvi": 0.85,
            "std_ndvi": 0.12,
        }
        results.append(result)

    results_df = pd.DataFrame(results)
    print("\n=== Forest Stand Health Summary ===")
    print(results_df.to_string(index=False))

    # Identify stands needing attention
    low_health_threshold = 0.6
    attention_stands = results_df[results_df["mean_ndvi"] < low_health_threshold]
    if not attention_stands.empty:
        print(f"\n⚠️ Stands requiring attention (NDVI < {low_health_threshold}):")
        for _, stand in attention_stands.iterrows():
            print(
                f"  - {stand['stand_id']}: {stand['forest_type']} (NDVI = {stand['mean_ndvi']:.2f})"
            )

    return results_df


def extract_watershed_statistics():
    """
    Extract statistics for watershed-level forest monitoring.

    Use case: Watershed managers need to monitor forest cover
    and health across entire drainage basins.
    """

    print("\n=== Watershed-Level Forest Statistics ===\n")

    # Create sample watershed polygon
    watershed_coords = [
        [-122.6, 45.4],
        [-122.4, 45.4],
        [-122.3, 45.5],
        [-122.4, 45.6],
        [-122.6, 45.6],
        [-122.7, 45.5],
        [-122.6, 45.4],
    ]

    watershed_polygon = Polygon(watershed_coords)

    # Create GeoDataFrame
    watershed_gdf = gpd.GeoDataFrame(
        [{"watershed_id": "CEDAR_RIVER", "area_km2": 245.8, "forest_cover_pct": 78.5}],
        geometry=[watershed_polygon],
        crs="EPSG:4326",
    )

    print(f"Watershed: {watershed_gdf['watershed_id'].iloc[0]}")
    print(f"Area: {watershed_gdf['area_km2'].iloc[0]} km²")
    print(f"Forest cover: {watershed_gdf['forest_cover_pct'].iloc[0]}%")

    # Calculate statistics for different forest metrics
    print("\nCalculating forest statistics...")

    # Simulated extraction results
    stats = {
        "Mean Canopy Cover": "72.3%",
        "Mean NDVI": "0.68",
        "Mean EVI": "0.45",
        "Forest Loss (Annual)": "0.8%",
        "Forest Gain (Annual)": "0.3%",
        "Disturbance Events": "2",
        "Fire Risk Level": "Moderate",
    }

    print("\nWatershed Forest Metrics:")
    for metric, value in stats.items():
        print(f"  {metric}: {value}")

    return watershed_gdf, stats


def compare_forest_parcels():
    """
    Compare multiple forest parcels for management decisions.

    Use case: Compare different parcels for timber harvest planning
    or conservation prioritization.
    """

    print("\n=== Comparing Forest Parcels ===\n")

    # Create sample forest parcels
    parcels = []
    parcel_data = [
        {"id": "PARCEL_A", "lat": 45.5, "lon": -122.5, "size": 50},
        {"id": "PARCEL_B", "lat": 45.6, "lon": -122.4, "size": 75},
        {"id": "PARCEL_C", "lat": 45.7, "lon": -122.6, "size": 60},
    ]

    for p in parcel_data:
        # Create a square polygon around center point
        size_deg = p["size"] / 111000  # Convert size to degrees (rough)
        coords = [
            [p["lon"] - size_deg / 2, p["lat"] - size_deg / 2],
            [p["lon"] + size_deg / 2, p["lat"] - size_deg / 2],
            [p["lon"] + size_deg / 2, p["lat"] + size_deg / 2],
            [p["lon"] - size_deg / 2, p["lat"] + size_deg / 2],
            [p["lon"] - size_deg / 2, p["lat"] - size_deg / 2],
        ]
        parcels.append(
            {"parcel_id": p["id"], "geometry": Polygon(coords), "area_ha": p["size"]}
        )

    parcels_gdf = gpd.GeoDataFrame(parcels, crs="EPSG:4326")

    # Extract and compare metrics
    comparison_data = []
    for idx, parcel in parcels_gdf.iterrows():
        # Simulated extraction results
        metrics = {
            "parcel_id": parcel["parcel_id"],
            "area_ha": parcel["area_ha"],
            "mean_ndvi": 0.55 + np.random.random() * 0.3,
            "biomass_tons": parcel["area_ha"] * (200 + np.random.random() * 100),
            "carbon_tons": parcel["area_ha"] * (100 + np.random.random() * 50),
            "species_diversity": np.random.choice(["Low", "Medium", "High"]),
            "accessibility": np.random.choice(["Easy", "Moderate", "Difficult"]),
            "conservation_value": np.random.randint(1, 11),  # 1-10 scale
        }
        comparison_data.append(metrics)

    comparison_df = pd.DataFrame(comparison_data)

    print("Forest Parcel Comparison:")
    print(comparison_df.to_string(index=False))

    # Rank parcels for different objectives
    print("\n=== Management Recommendations ===")

    # For timber harvest (high biomass, easy access)
    timber_score = comparison_df.copy()
    timber_score["access_score"] = timber_score["accessibility"].map(
        {"Easy": 3, "Moderate": 2, "Difficult": 1}
    )
    timber_score["timber_priority"] = (
        timber_score["biomass_tons"] * timber_score["access_score"]
    )
    best_timber = timber_score.nlargest(1, "timber_priority")["parcel_id"].iloc[0]
    print(f"Best for timber harvest: {best_timber}")

    # For conservation (high diversity, high conservation value)
    best_conservation = comparison_df.nlargest(1, "conservation_value")[
        "parcel_id"
    ].iloc[0]
    print(f"Best for conservation: {best_conservation}")

    # For carbon credits (high carbon storage)
    best_carbon = comparison_df.nlargest(1, "carbon_tons")["parcel_id"].iloc[0]
    print(f"Best for carbon credits: {best_carbon}")

    return comparison_df


def main():
    """Run area-based extraction examples."""

    print("=" * 60)
    print("SKIBA - Area-Based Forest Data Extraction")
    print("=" * 60)
    print()

    try:
        # Example 1: Forest stands
        stand_results = extract_data_for_forest_stands()

        # Example 2: Watershed statistics
        watershed_gdf, watershed_stats = extract_watershed_statistics()

        # Example 3: Parcel comparison
        parcel_comparison = compare_forest_parcels()

        print("\n✅ Area extraction examples completed!")
        print("\nThese examples demonstrate:")
        print("- Forest stand health monitoring")
        print("- Watershed-level statistics")
        print("- Multi-parcel comparison for management decisions")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nNote: These are conceptual demonstrations.")
        print("For actual Earth Engine extraction, ensure:")
        print("1. Earth Engine is properly authenticated")
        print("2. Valid GeoJSON/shapefiles are provided")
        print("3. Appropriate datasets and date ranges are selected")


if __name__ == "__main__":
    main()
