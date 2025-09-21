#!/usr/bin/env python
"""
Complete Point Extraction Example
==================================

This comprehensive example demonstrates forest monitoring point extraction with three modes:
1. DEMO MODE - Run with simulated data (no authentication needed)
2. INTERACTIVE MODE - Choose settings interactively
3. REAL MODE - Use actual Google Earth Engine data

Perfect for foresters who need to monitor vegetation indices at specific locations.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os
import sys
import time
import argparse

# Try imports for availability checking
try:
    from skiba.point_extraction import point_extraction

    SKIBA_AVAILABLE = True
except ImportError:
    SKIBA_AVAILABLE = False
    print("⚠️ Note: skiba package not found. Install with: pip install skiba")

try:
    import ee

    EE_AVAILABLE = True
except ImportError:
    EE_AVAILABLE = False
    print(
        "⚠️ Note: earthengine-api not found. Install with: pip install earthengine-api"
    )


# ==============================================================================
# SHARED UTILITY FUNCTIONS
# ==============================================================================


def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f" 🌲 {title} 🌲".center(70))
    print("=" * 70)


def get_default_forest_points():
    """Get default example forest monitoring points from US National Parks."""
    return pd.DataFrame(
        {
            "plot_ID": ["GSMNP_001", "YOSE_002", "YELL_003", "GLAC_004", "OLYM_005"],
            "LAT": [35.6532, 37.8651, 44.4280, 48.7596, 47.8021],
            "LON": [-83.5070, -119.5383, -110.5885, -113.7870, -123.6044],
            "forest_type": [
                "Mixed Deciduous",
                "Coniferous",
                "Lodgepole Pine",
                "Subalpine Fir",
                "Temperate Rainforest",
            ],
            "location": [
                "Great Smoky Mountains",
                "Yosemite",
                "Yellowstone",
                "Glacier",
                "Olympic",
            ],
        }
    )


def analyze_forest_health(results):
    """Analyze and display forest health metrics from extraction results."""
    print("\n" + "=" * 60)
    print("🌲 FOREST HEALTH ANALYSIS")
    print("=" * 60)

    if results is None or results.empty:
        print("❌ No results to analyze")
        return

    print(f"\n📊 Data Summary:")
    print(f"  • Points analyzed: {len(results)}")
    print(f"  • Available metrics: {', '.join(results.columns[:5])}...")

    if "NDVI" in results.columns:
        print(f"\n🌿 NDVI Statistics:")
        print(f"  • Mean:   {results['NDVI'].mean():.3f}")
        print(f"  • Median: {results['NDVI'].median():.3f}")
        print(f"  • Min:    {results['NDVI'].min():.3f}")
        print(f"  • Max:    {results['NDVI'].max():.3f}")
        print(f"  • Std:    {results['NDVI'].std():.3f}")

        # Categorize forest health
        def get_health_status(ndvi):
            if ndvi >= 0.7:
                return "Excellent", "🟢"
            elif ndvi >= 0.5:
                return "Good", "🔵"
            elif ndvi >= 0.3:
                return "Moderate", "🟡"
            else:
                return "Poor", "🔴"

        print("\n🏥 Forest Health Status:")
        results["health_status"] = results["NDVI"].apply(
            lambda x: get_health_status(x)[0]
        )

        for _, row in results.iterrows():
            status, emoji = get_health_status(row["NDVI"])
            location = row.get("location", row.get("forest_type", "Unknown"))
            print(f"  {emoji} {row['plot_ID']}: {status}")
            print(f"     Location: {location}")
            print(f"     NDVI: {row['NDVI']:.3f}")

        # Identify areas needing attention
        low_threshold = 0.5
        problem_areas = results[results["NDVI"] < low_threshold]
        if not problem_areas.empty:
            print(f"\n⚠️ Areas Requiring Attention (NDVI < {low_threshold}):")
            for _, area in problem_areas.iterrows():
                print(f"  • {area['plot_ID']}: NDVI = {area['NDVI']:.3f}")
                print(f"    Recommended: Field inspection and assessment")

    return results


def calculate_vegetation_indices(results):
    """Calculate various vegetation indices from band values."""
    print("\n📐 Calculating Additional Vegetation Indices...")

    indices_calculated = []

    # NDVI - Already calculated usually, but verify
    if "B4" in results.columns and "B8" in results.columns:  # Sentinel-2
        results["NDVI"] = (results["B8"] - results["B4"]) / (
            results["B8"] + results["B4"]
        )
        indices_calculated.append("NDVI")
    elif "B4" in results.columns and "B5" in results.columns:  # Landsat
        results["NDVI"] = (results["B5"] - results["B4"]) / (
            results["B5"] + results["B4"]
        )
        indices_calculated.append("NDVI")

    # EVI - Enhanced Vegetation Index
    if all(b in results.columns for b in ["B2", "B4", "B8"]):  # Sentinel-2
        results["EVI"] = 2.5 * (
            (results["B8"] - results["B4"])
            / (results["B8"] + 6 * results["B4"] - 7.5 * results["B2"] + 1)
        )
        indices_calculated.append("EVI")

    # SAVI - Soil Adjusted Vegetation Index
    if "B4" in results.columns and "B8" in results.columns:
        L = 0.5  # Soil brightness correction
        results["SAVI"] = (
            (results["B8"] - results["B4"]) / (results["B8"] + results["B4"] + L)
        ) * (1 + L)
        indices_calculated.append("SAVI")

    # GNDVI - Green NDVI
    if "B3" in results.columns and "B8" in results.columns:
        results["GNDVI"] = (results["B8"] - results["B3"]) / (
            results["B8"] + results["B3"]
        )
        indices_calculated.append("GNDVI")

    if indices_calculated:
        print(f"  ✅ Calculated: {', '.join(indices_calculated)}")
    else:
        print(f"  ⚠️ Insufficient bands for index calculation")

    return results


# ==============================================================================
# MODE 1: DEMO MODE (with simulated data)
# ==============================================================================


def simulate_extraction(
    forest_points, dataset_name="SIMULATED", start_date=None, end_date=None
):
    """Simulate Earth Engine extraction for demonstration purposes."""
    print("\n🔄 Generating simulated forest monitoring data...")

    # Simulate processing
    for i in range(3):
        print(f"  Processing{'.' * (i+1)}", end="\r")
        time.sleep(0.3)

    results = forest_points.copy()

    # Base NDVI values by forest type
    ndvi_base = {
        "Mixed Deciduous": 0.75,
        "Coniferous": 0.65,
        "Lodgepole Pine": 0.60,
        "Subalpine Fir": 0.55,
        "Temperate Rainforest": 0.80,
        "Oak-Hickory": 0.70,
        "Pine": 0.60,
    }

    # Seasonal adjustment
    if start_date:
        month = start_date.month
        seasonal_factor = 1.0 - abs(month - 7) * 0.08  # Peak in July
    else:
        seasonal_factor = 0.9

    # Generate realistic values
    for idx, row in results.iterrows():
        forest_type = row.get("forest_type", "Unknown")
        base_ndvi = ndvi_base.get(forest_type, 0.65)

        # Add variation
        ndvi = base_ndvi * seasonal_factor + np.random.normal(0, 0.05)
        results.at[idx, "NDVI"] = np.clip(ndvi, 0, 1)

        # Simulate band values (Sentinel-2 bands)
        results.at[idx, "B2"] = 0.04 + np.random.normal(0, 0.01)  # Blue
        results.at[idx, "B3"] = 0.06 + np.random.normal(0, 0.01)  # Green
        results.at[idx, "B4"] = 0.08 + np.random.normal(0, 0.02)  # Red
        results.at[idx, "B8"] = 0.40 + np.random.normal(0, 0.03)  # NIR

        # Add metadata
        results.at[idx, "cloud_cover_%"] = np.random.randint(0, 30)
        results.at[idx, "dataset"] = dataset_name
        results.at[idx, "extraction_date"] = datetime.now().strftime("%Y-%m-%d")

    print("\n✅ Simulation complete!")
    return results


def run_demo_mode():
    """Run the demonstration mode with simulated data."""
    print_header("DEMO MODE - SIMULATED DATA")

    print("\n📝 This mode demonstrates the workflow without requiring Earth Engine.")
    print("   Perfect for testing and learning!\n")

    # Get forest points
    forest_points = get_default_forest_points()
    print(f"📍 Using {len(forest_points)} example forest monitoring points:")
    print(forest_points[["plot_ID", "location", "forest_type"]].to_string(index=False))

    # Set parameters
    start_date = datetime(2024, 7, 1)
    end_date = datetime(2024, 8, 31)
    print(f"\n📅 Date Range: {start_date.date()} to {end_date.date()}")

    # Simulate extraction
    results = simulate_extraction(forest_points, "DEMO_S2", start_date, end_date)

    # Calculate indices
    results = calculate_vegetation_indices(results)

    # Analyze health
    results = analyze_forest_health(results)

    # Save results
    output_file = "demo_forest_monitoring_results.csv"
    results.to_csv(output_file, index=False)
    print(f"\n💾 Results saved to: {output_file}")

    return results


# ==============================================================================
# MODE 2: REAL EARTH ENGINE MODE
# ==============================================================================


def setup_earth_engine(project_id=None):
    """Setup and authenticate Earth Engine."""
    if not EE_AVAILABLE:
        print("❌ Earth Engine API not installed!")
        return False

    try:
        if not project_id:
            print("\n🔑 Earth Engine Authentication Required")
            print("   1. You need a Google Earth Engine account")
            print("   2. Visit: https://earthengine.google.com/signup/")

            auth_choice = input("\n➤ Authenticate now? (y/n): ").lower()
            if auth_choice != "y":
                return False

            ee.Authenticate()
            project_id = input("➤ Enter your GEE Project ID: ").strip()

        ee.Initialize(project=project_id)
        print("✅ Earth Engine initialized successfully!")
        return True

    except Exception as e:
        print(f"❌ Earth Engine setup failed: {e}")
        return False


def extract_real_ee_data(forest_points, dataset, start_date, end_date):
    """Extract real data from Google Earth Engine."""
    if not SKIBA_AVAILABLE:
        print("❌ skiba package not available")
        return None

    print("\n🛰️ Extracting data from Google Earth Engine...")
    print(f"   Dataset: {dataset}")
    print(f"   Points: {len(forest_points)}")

    try:
        # Save points temporarily
        temp_file = "temp_extraction_points.csv"
        forest_points.to_csv(temp_file, index=False)

        # Initialize extraction
        pe = point_extraction()

        # Perform extraction
        results = pe.get_coordinate_data(
            data=temp_file, geedata=dataset, start_date=start_date, end_date=end_date
        )

        # Cleanup
        if os.path.exists(temp_file):
            os.remove(temp_file)

        print("✅ Extraction complete!")
        return results

    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        return None


def run_real_mode(project_id=None):
    """Run extraction with real Earth Engine data."""
    print_header("REAL MODE - GOOGLE EARTH ENGINE")

    # Setup Earth Engine
    if not setup_earth_engine(project_id):
        print("⚠️ Falling back to demo mode...")
        return run_demo_mode()

    # Get forest points
    forest_points = get_default_forest_points()
    print(f"\n📍 Using {len(forest_points)} forest monitoring points")

    # Set parameters
    dataset = "COPERNICUS/S2_SR_HARMONIZED"
    start_date = datetime(2024, 6, 1)
    end_date = datetime(2024, 8, 31)

    # Extract real data
    results = extract_real_ee_data(forest_points, dataset, start_date, end_date)

    if results is None:
        print("\n⚠️ Using simulated data as fallback...")
        results = simulate_extraction(forest_points, dataset, start_date, end_date)

    # Analyze
    results = analyze_forest_health(results)

    # Save
    output_file = "real_forest_monitoring_results.csv"
    results.to_csv(output_file, index=False)
    print(f"\n💾 Results saved to: {output_file}")

    return results


# ==============================================================================
# MODE 3: INTERACTIVE MODE
# ==============================================================================


def run_interactive_mode():
    """Run the interactive mode where users make choices."""
    print_header("INTERACTIVE MODE")

    print("\n🎯 Choose your data source:")
    print("   1. Demo data (no authentication needed)")
    print("   2. Real Earth Engine data")
    print("   3. Custom CSV file")

    choice = input("\n➤ Select option (1-3): ").strip()

    # Get forest points based on choice
    if choice == "3":
        csv_path = input("➤ Enter CSV path: ").strip()
        try:
            forest_points = pd.read_csv(csv_path)
            print(f"✅ Loaded {len(forest_points)} points")
        except Exception as e:
            print(f"❌ Error loading CSV: {e}")
            forest_points = get_default_forest_points()
    else:
        forest_points = get_default_forest_points()

    # Choose dataset
    print("\n📡 Select dataset:")
    print("   1. Sentinel-2 (10m resolution)")
    print("   2. Landsat 8 (30m resolution)")
    print("   3. MODIS (250m resolution)")

    dataset_choice = input("➤ Select (1-3): ").strip()
    datasets = {
        "1": "COPERNICUS/S2_SR_HARMONIZED",
        "2": "LANDSAT/LC08/C02/T1_L2",
        "3": "MODIS/006/MOD13Q1",
    }
    dataset = datasets.get(dataset_choice, datasets["1"])

    # Date range
    print("\n📅 Date range:")
    print("   1. Last 30 days")
    print("   2. Summer 2024")
    print("   3. Custom")

    date_choice = input("➤ Select (1-3): ").strip()

    if date_choice == "1":
        end_date = datetime.now()
        start_date = end_date - pd.Timedelta(days=30)
    elif date_choice == "3":
        start_str = input("➤ Start date (YYYY-MM-DD): ").strip()
        end_str = input("➤ End date (YYYY-MM-DD): ").strip()
        start_date = datetime.strptime(start_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_str, "%Y-%m-%d")
    else:
        start_date = datetime(2024, 6, 1)
        end_date = datetime(2024, 8, 31)

    # Extract based on initial choice
    if choice == "2":
        # Try real extraction
        if setup_earth_engine():
            results = extract_real_ee_data(forest_points, dataset, start_date, end_date)
        else:
            results = None

        if results is None:
            print("⚠️ Using demo data...")
            results = simulate_extraction(forest_points, dataset, start_date, end_date)
    else:
        # Use demo
        results = simulate_extraction(forest_points, dataset, start_date, end_date)

    # Analyze
    results = analyze_forest_health(results)

    # Save option
    save_choice = input("\n➤ Save results? (y/n): ").lower()
    if save_choice == "y":
        filename = input("➤ Filename (default: results.csv): ").strip()
        if not filename:
            filename = "results.csv"
        if not filename.endswith(".csv"):
            filename += ".csv"
        results.to_csv(filename, index=False)
        print(f"✅ Saved to: {filename}")

    return results


# ==============================================================================
# MAIN PROGRAM
# ==============================================================================


def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="Forest Monitoring Point Extraction Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --demo              # Run with simulated data
  %(prog)s --interactive       # Choose options interactively
  %(prog)s --real              # Use real Earth Engine data
  %(prog)s --real --project my-ee-project  # Specify EE project
        """,
    )

    parser.add_argument(
        "--demo", action="store_true", help="Run demo mode with simulated data"
    )
    parser.add_argument(
        "--interactive", action="store_true", help="Run interactive mode"
    )
    parser.add_argument(
        "--real", action="store_true", help="Use real Earth Engine data"
    )
    parser.add_argument("--project", type=str, help="Google Earth Engine project ID")

    args = parser.parse_args()

    # Print system status
    print("🔍 System Check:")
    print(f"  • skiba: {'✅ Installed' if SKIBA_AVAILABLE else '❌ Not installed'}")
    print(
        f"  • earthengine-api: {'✅ Installed' if EE_AVAILABLE else '❌ Not installed'}"
    )

    try:
        # Run based on arguments
        if args.interactive:
            run_interactive_mode()
        elif args.real:
            run_real_mode(args.project)
        else:
            # Default to demo
            run_demo_mode()

        print("\n✅ Complete! Thank you for using SKIBA!")

    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("See TROUBLESHOOTING.md for help")


if __name__ == "__main__":
    main()
