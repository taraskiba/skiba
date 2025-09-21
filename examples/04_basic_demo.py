#!/usr/bin/env python
"""
Basic Point Extraction Example - Demonstration Version
=======================================================

This is a demonstration version that can run without Earth Engine authentication.
It shows the concepts and workflow using simulated data.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys

# Try to import skiba, but provide fallback
try:
    from skiba.point_extraction import point_extraction

    SKIBA_AVAILABLE = True
except ImportError:
    SKIBA_AVAILABLE = False
    print("Note: skiba package not found. Running in demonstration mode.")

# Try to import Earth Engine
try:
    import ee

    EE_AVAILABLE = True
except ImportError:
    EE_AVAILABLE = False
    print("Note: earthengine-api not installed. Running with simulated data.")


def simulate_ndvi_data(points_df, start_date, end_date):
    """
    Simulate NDVI data for demonstration purposes.

    This creates realistic NDVI values based on forest type and season.
    """
    print("📊 Simulating NDVI data for demonstration...")

    # Base NDVI values by forest type
    ndvi_base = {
        "Mixed Deciduous": 0.75,
        "Coniferous": 0.65,
        "Oak-Hickory": 0.70,
        "Pine": 0.60,
        "Default": 0.65,
    }

    # Seasonal variation (simplified)
    month = start_date.month
    seasonal_factor = {
        1: 0.3,
        2: 0.3,
        3: 0.4,  # Winter/Early Spring
        4: 0.6,
        5: 0.8,
        6: 0.95,  # Spring/Early Summer
        7: 1.0,
        8: 0.95,
        9: 0.85,  # Summer/Early Fall
        10: 0.7,
        11: 0.5,
        12: 0.35,  # Fall/Winter
    }.get(month, 0.7)

    results = points_df.copy()

    # Generate NDVI values
    for idx, row in results.iterrows():
        forest_type = row.get("forest_type", "Default")
        base_value = ndvi_base.get(forest_type, ndvi_base["Default"])

        # Apply seasonal factor and add random variation
        ndvi = base_value * seasonal_factor + np.random.normal(0, 0.05)
        ndvi = np.clip(ndvi, -1, 1)  # Ensure valid NDVI range

        results.at[idx, "NDVI"] = ndvi

        # Add simulated band values for educational purposes
        results.at[idx, "B4_RED"] = 0.05 + np.random.normal(0, 0.01)
        results.at[idx, "B5_NIR"] = 0.40 + np.random.normal(0, 0.02)
        results.at[idx, "B3_GREEN"] = 0.08 + np.random.normal(0, 0.01)

        # Add metadata
        results.at[idx, "extraction_date"] = datetime.now().strftime("%Y-%m-%d")
        results.at[idx, "dataset"] = "SIMULATED_S2"

    return results


def extract_ndvi_for_forest_points(use_real_ee=False):
    """
    Extract NDVI values for forest monitoring points.

    Args:
        use_real_ee (bool): If True, attempt to use real Earth Engine data.
                           If False or if EE fails, use simulated data.
    """

    print("\n" + "=" * 60)
    print("📍 FOREST MONITORING POINT EXTRACTION")
    print("=" * 60)

    # Define forest monitoring points
    # These represent real forest locations in the US
    forest_points = pd.DataFrame(
        {
            "plot_ID": ["GSMNP_001", "GRCA_002", "SHEN_003", "YOSE_004"],
            "LAT": [35.6532, 36.0544, 38.5258, 37.8651],
            "LON": [-83.5070, -112.1401, -78.4347, -119.5383],
            "forest_type": ["Mixed Deciduous", "Coniferous", "Oak-Hickory", "Pine"],
            "park": ["Great Smoky Mountains", "Grand Canyon", "Shenandoah", "Yosemite"],
        }
    )

    print("\n📋 Forest Monitoring Points:")
    print(forest_points[["plot_ID", "park", "forest_type"]].to_string(index=False))

    # Save to CSV
    output_file = "forest_monitoring_points.csv"
    forest_points.to_csv(output_file, index=False)
    print(f"\n💾 Saved points to: {output_file}")

    # Set date range
    start_date = datetime(2024, 7, 1)  # Summer season
    end_date = datetime(2024, 8, 31)

    print(f"\n📅 Date Range: {start_date.date()} to {end_date.date()}")

    # Try to use real Earth Engine if requested and available
    if use_real_ee and SKIBA_AVAILABLE and EE_AVAILABLE:
        try:
            print("\n🌍 Attempting to connect to Google Earth Engine...")

            # Initialize Earth Engine
            ee.Initialize()

            # Use skiba for extraction
            pe = point_extraction()
            results = pe.get_coordinate_data(
                data=output_file,
                geedata="COPERNICUS/S2_SR_HARMONIZED",
                start_date=start_date,
                end_date=end_date,
            )

            print("✅ Successfully extracted data from Earth Engine!")

        except Exception as e:
            print(f"⚠️ Earth Engine extraction failed: {e}")
            print("📊 Falling back to simulated data...")
            results = simulate_ndvi_data(forest_points, start_date, end_date)
    else:
        # Use simulated data
        results = simulate_ndvi_data(forest_points, start_date, end_date)

    # Analyze results
    analyze_forest_health(results)

    # Save results
    results_file = "forest_ndvi_results.csv"
    results.to_csv(results_file, index=False)
    print(f"\n💾 Results saved to: {results_file}")

    return results


def analyze_forest_health(results):
    """Analyze and display forest health metrics."""

    print("\n" + "=" * 60)
    print("🌲 FOREST HEALTH ANALYSIS")
    print("=" * 60)

    print(f"\n📊 Data Summary:")
    print(f"  • Points analyzed: {len(results)}")
    print(f"  • Available metrics: NDVI, Band Values")

    if "NDVI" in results.columns:
        print(f"\n🌿 NDVI Statistics:")
        print(f"  • Mean NDVI: {results['NDVI'].mean():.3f}")
        print(f"  • Min NDVI:  {results['NDVI'].min():.3f}")
        print(f"  • Max NDVI:  {results['NDVI'].max():.3f}")
        print(f"  • Std Dev:   {results['NDVI'].std():.3f}")

        # Forest health categories
        print("\n🏥 Forest Health Categories:")

        def categorize_health(ndvi):
            if ndvi >= 0.7:
                return "Excellent"
            elif ndvi >= 0.5:
                return "Good"
            elif ndvi >= 0.3:
                return "Moderate"
            else:
                return "Poor"

        results["health_status"] = results["NDVI"].apply(categorize_health)

        for _, row in results.iterrows():
            status_emoji = {
                "Excellent": "🟢",
                "Good": "🔵",
                "Moderate": "🟡",
                "Poor": "🔴",
            }.get(row["health_status"], "⚪")

            print(
                f"  {status_emoji} {row['plot_ID']}: {row['health_status']} (NDVI = {row['NDVI']:.3f})"
            )

        # Identify areas needing attention
        low_ndvi_threshold = 0.5
        problem_plots = results[results["NDVI"] < low_ndvi_threshold]

        if not problem_plots.empty:
            print(f"\n⚠️ Plots Requiring Attention (NDVI < {low_ndvi_threshold}):")
            for _, plot in problem_plots.iterrows():
                print(f"  • {plot['plot_ID']} in {plot.get('park', 'Unknown')}")
                print(f"    - Forest Type: {plot.get('forest_type', 'Unknown')}")
                print(f"    - NDVI: {plot['NDVI']:.3f}")
                print(f"    - Recommended Action: Field inspection needed")

    # Display sample of results
    print("\n📋 Sample Results:")
    display_columns = ["plot_ID", "NDVI", "health_status"]
    available_columns = [col for col in display_columns if col in results.columns]
    print(results[available_columns].head().to_string(index=False))


def demonstrate_vegetation_indices():
    """Demonstrate calculation of various vegetation indices."""

    print("\n" + "=" * 60)
    print("📐 VEGETATION INDEX CALCULATIONS")
    print("=" * 60)

    # Create sample band values
    sample_data = pd.DataFrame(
        {
            "plot_ID": ["DEMO_1", "DEMO_2", "DEMO_3"],
            "B2_BLUE": [0.04, 0.05, 0.06],
            "B3_GREEN": [0.06, 0.07, 0.08],
            "B4_RED": [0.05, 0.08, 0.10],
            "B5_NIR": [0.35, 0.40, 0.30],
            "B6_SWIR1": [0.15, 0.18, 0.20],
        }
    )

    print("\n📊 Sample Band Values:")
    print(sample_data.to_string(index=False))

    # Calculate vegetation indices
    print("\n🧮 Calculating Vegetation Indices...")

    # NDVI - Normalized Difference Vegetation Index
    sample_data["NDVI"] = (sample_data["B5_NIR"] - sample_data["B4_RED"]) / (
        sample_data["B5_NIR"] + sample_data["B4_RED"]
    )

    # GNDVI - Green NDVI
    sample_data["GNDVI"] = (sample_data["B5_NIR"] - sample_data["B3_GREEN"]) / (
        sample_data["B5_NIR"] + sample_data["B3_GREEN"]
    )

    # EVI - Enhanced Vegetation Index (simplified)
    sample_data["EVI"] = 2.5 * (
        (sample_data["B5_NIR"] - sample_data["B4_RED"])
        / (
            sample_data["B5_NIR"]
            + 6 * sample_data["B4_RED"]
            - 7.5 * sample_data["B2_BLUE"]
            + 1
        )
    )

    # SAVI - Soil Adjusted Vegetation Index
    L = 0.5  # Soil brightness correction factor
    sample_data["SAVI"] = (
        (sample_data["B5_NIR"] - sample_data["B4_RED"])
        / (sample_data["B5_NIR"] + sample_data["B4_RED"] + L)
    ) * (1 + L)

    # NDMI - Normalized Difference Moisture Index
    sample_data["NDMI"] = (sample_data["B5_NIR"] - sample_data["B6_SWIR1"]) / (
        sample_data["B5_NIR"] + sample_data["B6_SWIR1"]
    )

    print("\n📈 Calculated Indices:")
    index_columns = ["plot_ID", "NDVI", "GNDVI", "EVI", "SAVI", "NDMI"]
    print(sample_data[index_columns].round(3).to_string(index=False))

    print("\n📖 Index Interpretations:")
    print("  • NDVI:  Vegetation density (Higher = Denser)")
    print("  • GNDVI: Chlorophyll content (Higher = Greener)")
    print("  • EVI:   Enhanced vegetation (Better for dense canopy)")
    print("  • SAVI:  Soil-adjusted (Better for sparse vegetation)")
    print("  • NDMI:  Moisture content (Higher = More water)")

    return sample_data


def main():
    """Run the demonstration examples."""

    print("=" * 70)
    print(" 🌲 SKIBA - FOREST MONITORING DEMONSTRATION 🌲")
    print("=" * 70)
    print("\nThis demonstration shows how to use skiba for forest monitoring.")
    print("It can run with or without Earth Engine authentication.\n")

    # Check environment
    print("🔍 Environment Check:")
    print(f"  • skiba installed: {'✅' if SKIBA_AVAILABLE else '❌'}")
    print(f"  • earthengine-api installed: {'✅' if EE_AVAILABLE else '❌'}")

    if not SKIBA_AVAILABLE:
        print("\n💡 To install skiba: pip install skiba")
    if not EE_AVAILABLE:
        print("\n💡 To install Earth Engine: pip install earthengine-api")

    try:
        # Example 1: Extract NDVI for forest points
        print("\n" + "=" * 70)
        print("EXAMPLE 1: Forest Point NDVI Extraction")
        print("=" * 70)

        # Use simulated data by default for demonstration
        results = extract_ndvi_for_forest_points(use_real_ee=False)

        # Example 2: Demonstrate vegetation index calculations
        print("\n" + "=" * 70)
        print("EXAMPLE 2: Vegetation Index Calculations")
        print("=" * 70)

        index_results = demonstrate_vegetation_indices()

        # Summary
        print("\n" + "=" * 70)
        print("✅ DEMONSTRATION COMPLETE!")
        print("=" * 70)

        print("\n📚 What you learned:")
        print("  1. How to define forest monitoring points")
        print("  2. How to extract NDVI data (real or simulated)")
        print("  3. How to analyze forest health metrics")
        print("  4. How to calculate various vegetation indices")

        print("\n🚀 Next Steps:")
        print("  1. Install and authenticate Earth Engine for real data")
        print("  2. Modify coordinates for your study area")
        print("  3. Adjust date ranges for your analysis period")
        print("  4. Add additional vegetation indices as needed")

        print("\n📁 Generated Files:")
        print("  • forest_monitoring_points.csv - Input coordinates")
        print("  • forest_ndvi_results.csv - Extraction results")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()

        print("\n💡 Troubleshooting Tips:")
        print("  1. Check that all dependencies are installed")
        print("  2. Verify file permissions in current directory")
        print("  3. See TROUBLESHOOTING.md for common solutions")


if __name__ == "__main__":
    main()
