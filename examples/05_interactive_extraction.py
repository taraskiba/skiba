#!/usr/bin/env python
"""
Interactive Forest Point Extraction Example
============================================

This interactive example lets you choose between:
1. Demo mode with simulated data (no authentication needed)
2. Real Earth Engine data (requires authentication)
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os
import sys
import time

# Check available imports
try:
    from skiba.point_extraction import point_extraction
    SKIBA_AVAILABLE = True
except ImportError:
    SKIBA_AVAILABLE = False

try:
    import ee
    EE_AVAILABLE = True
except ImportError:
    EE_AVAILABLE = False


def print_header():
    """Print a nice header for the application."""
    print("\n" + "="*70)
    print(" 🌲 SKIBA - INTERACTIVE FOREST MONITORING TOOL 🌲".center(70))
    print("="*70)


def get_user_choice():
    """Get user's choice for data source."""
    print("\n🌍 DATA SOURCE OPTIONS:")
    print("-" * 40)
    print("1. 📊 Demo Mode (Simulated data - no authentication needed)")
    print("2. 🛰️  Real Mode (Google Earth Engine - requires authentication)")
    print("3. ❌ Exit")

    while True:
        choice = input("\n➤ Select an option (1-3): ").strip()
        if choice in ['1', '2', '3']:
            return choice
        print("❌ Invalid choice. Please enter 1, 2, or 3.")


def setup_earth_engine():
    """Interactive Earth Engine setup."""
    print("\n" + "="*60)
    print("🛰️  GOOGLE EARTH ENGINE SETUP")
    print("="*60)

    if not EE_AVAILABLE:
        print("\n❌ Earth Engine API not installed!")
        print("📦 To install: pip install earthengine-api")
        return False

    print("\n📋 Prerequisites:")
    print("  1. Google Earth Engine account (signup.earthengine.google.com)")
    print("  2. Google Cloud Project with Earth Engine API enabled")
    print("  3. Authentication credentials")

    print("\n🔐 Authentication Options:")
    print("  1. Browser authentication (recommended for first-time)")
    print("  2. Use existing credentials")
    print("  3. Skip (use demo mode)")

    auth_choice = input("\n➤ Select authentication method (1-3): ").strip()

    if auth_choice == '3':
        return False

    try:
        if auth_choice == '1':
            print("\n🌐 Opening browser for authentication...")
            print("📝 Please follow these steps:")
            print("  1. A browser window will open")
            print("  2. Log in with your Google account")
            print("  3. Authorize Earth Engine")
            print("  4. Copy the authorization code")
            print("  5. Paste it here when prompted")

            input("\n➤ Press Enter to continue...")

            try:
                ee.Authenticate(force=True)
                print("✅ Authentication successful!")
            except Exception as e:
                print(f"❌ Authentication failed: {e}")
                return False

        # Get project ID
        print("\n🔧 Project Configuration:")
        print("  Find your project ID at: console.cloud.google.com")
        print("  Example: 'my-earth-engine-project'")

        project_id = input("\n➤ Enter your Google Cloud Project ID (or 'skip' for demo): ").strip()

        if project_id.lower() == 'skip':
            return False

        # Initialize Earth Engine
        print(f"\n🚀 Initializing Earth Engine with project: {project_id}")

        try:
            ee.Initialize(project=project_id)
            print("✅ Earth Engine initialized successfully!")

            # Test connection
            print("🧪 Testing connection...")
            test_image = ee.Image(1).getInfo()
            print("✅ Connection test passed!")

            return True

        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            print("\n💡 Common issues:")
            print("  • Project ID is incorrect")
            print("  • Earth Engine API not enabled for project")
            print("  • Authentication expired")
            return False

    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return False


def get_extraction_parameters():
    """Get user input for extraction parameters."""
    print("\n" + "="*60)
    print("⚙️  EXTRACTION PARAMETERS")
    print("="*60)

    # Dataset selection
    print("\n📡 Available Datasets:")
    datasets = {
        '1': ('COPERNICUS/S2_SR_HARMONIZED', 'Sentinel-2 (10m resolution, 5-day)'),
        '2': ('LANDSAT/LC08/C02/T1_L2', 'Landsat 8 (30m resolution, 16-day)'),
        '3': ('MODIS/006/MOD13Q1', 'MODIS NDVI (250m resolution, 16-day)'),
        '4': ('custom', 'Enter custom dataset ID')
    }

    for key, (dataset_id, description) in datasets.items():
        print(f"  {key}. {description}")

    dataset_choice = input("\n➤ Select dataset (1-4): ").strip()

    if dataset_choice == '4':
        dataset = input("➤ Enter custom dataset ID: ").strip()
    elif dataset_choice in datasets:
        dataset = datasets[dataset_choice][0]
    else:
        print("⚠️ Invalid choice, using Sentinel-2")
        dataset = 'COPERNICUS/S2_SR_HARMONIZED'

    # Date range selection
    print("\n📅 Date Range Selection:")
    print("  1. Last 30 days")
    print("  2. Last 3 months")
    print("  3. Summer 2024 (Jun-Aug)")
    print("  4. Custom date range")

    date_choice = input("\n➤ Select date range (1-4): ").strip()

    if date_choice == '1':
        end_date = datetime.now()
        start_date = end_date - pd.Timedelta(days=30)
    elif date_choice == '2':
        end_date = datetime.now()
        start_date = end_date - pd.Timedelta(days=90)
    elif date_choice == '3':
        start_date = datetime(2024, 6, 1)
        end_date = datetime(2024, 8, 31)
    else:
        print("\n📅 Enter custom date range (YYYY-MM-DD format):")
        start_str = input("➤ Start date: ").strip()
        end_str = input("➤ End date: ").strip()
        try:
            start_date = datetime.strptime(start_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_str, '%Y-%m-%d')
        except:
            print("⚠️ Invalid date format, using default range")
            start_date = datetime(2024, 6, 1)
            end_date = datetime(2024, 8, 31)

    print(f"\n✅ Selected: {dataset}")
    print(f"✅ Date range: {start_date.date()} to {end_date.date()}")

    return dataset, start_date, end_date


def get_forest_points():
    """Get forest monitoring points from user."""
    print("\n" + "="*60)
    print("📍 FOREST MONITORING POINTS")
    print("="*60)

    print("\n🌲 Point Selection Options:")
    print("  1. Use example forest locations (US National Parks)")
    print("  2. Enter custom coordinates")
    print("  3. Load from CSV file")

    point_choice = input("\n➤ Select option (1-3): ").strip()

    if point_choice == '2':
        # Custom coordinates
        print("\n📝 Enter custom coordinates (one per line)")
        print("Format: plot_id,latitude,longitude,forest_type")
        print("Example: PLOT_001,35.6532,-83.5070,Oak Forest")
        print("Type 'done' when finished:")

        points = []
        while True:
            line = input("➤ ").strip()
            if line.lower() == 'done':
                break
            try:
                parts = line.split(',')
                if len(parts) >= 3:
                    points.append({
                        'plot_ID': parts[0].strip(),
                        'LAT': float(parts[1].strip()),
                        'LON': float(parts[2].strip()),
                        'forest_type': parts[3].strip() if len(parts) > 3 else 'Unknown'
                    })
                    print(f"  ✅ Added {parts[0].strip()}")
            except:
                print("  ❌ Invalid format, skipping")

        if points:
            forest_points = pd.DataFrame(points)
        else:
            print("⚠️ No valid points entered, using defaults")
            forest_points = get_default_forest_points()

    elif point_choice == '3':
        # Load from CSV
        csv_path = input("\n➤ Enter CSV file path: ").strip()
        try:
            forest_points = pd.read_csv(csv_path)
            print(f"✅ Loaded {len(forest_points)} points from {csv_path}")
        except Exception as e:
            print(f"❌ Error loading CSV: {e}")
            print("⚠️ Using default points")
            forest_points = get_default_forest_points()
    else:
        # Use defaults
        forest_points = get_default_forest_points()

    # Display points
    print(f"\n📊 Using {len(forest_points)} monitoring points:")
    print(forest_points[['plot_ID', 'LAT', 'LON']].to_string(index=False))

    return forest_points


def get_default_forest_points():
    """Get default example forest points."""
    return pd.DataFrame({
        'plot_ID': ['GSMNP_001', 'YOSE_002', 'YELL_003', 'GLAC_004'],
        'LAT': [35.6532, 37.8651, 44.4280, 48.7596],
        'LON': [-83.5070, -119.5383, -110.5885, -113.7870],
        'forest_type': ['Mixed Deciduous', 'Coniferous', 'Lodgepole Pine', 'Subalpine Fir'],
        'location': ['Great Smoky Mountains', 'Yosemite', 'Yellowstone', 'Glacier']
    })


def simulate_extraction(forest_points, dataset, start_date, end_date):
    """Simulate data extraction for demo mode."""
    print("\n🔄 Simulating data extraction...")

    # Simulate processing time
    for i in range(3):
        print(f"  Processing{'.' * (i+1)}", end='\r')
        time.sleep(0.5)

    # Generate simulated data
    results = forest_points.copy()

    # Base NDVI by forest type
    ndvi_base = {
        'Mixed Deciduous': 0.75,
        'Coniferous': 0.65,
        'Lodgepole Pine': 0.60,
        'Subalpine Fir': 0.55,
        'Oak Forest': 0.70,
        'Pine': 0.60,
        'Unknown': 0.65
    }

    # Seasonal adjustment
    month = start_date.month
    seasonal_factor = 1.0 - abs(month - 7) * 0.08  # Peak in July

    for idx, row in results.iterrows():
        forest_type = row.get('forest_type', 'Unknown')
        base = ndvi_base.get(forest_type, 0.65)
        ndvi = base * seasonal_factor + np.random.normal(0, 0.05)
        results.at[idx, 'NDVI'] = np.clip(ndvi, 0, 1)

        # Add band values
        results.at[idx, 'B4_RED'] = 0.08 + np.random.normal(0, 0.02)
        results.at[idx, 'B8_NIR'] = 0.40 + np.random.normal(0, 0.03)
        results.at[idx, 'cloud_cover'] = np.random.randint(0, 30)

    print("\n✅ Simulation complete!")
    return results


def perform_real_extraction(forest_points, dataset, start_date, end_date):
    """Perform real Earth Engine extraction."""
    print("\n🔄 Extracting data from Google Earth Engine...")

    if not SKIBA_AVAILABLE:
        print("❌ skiba package not available")
        return None

    try:
        # Save points to CSV
        temp_csv = 'temp_forest_points.csv'
        forest_points.to_csv(temp_csv, index=False)

        # Initialize point extraction
        pe = point_extraction()

        # Perform extraction
        print(f"  Dataset: {dataset}")
        print(f"  Points: {len(forest_points)}")
        print(f"  Processing...")

        results = pe.get_coordinate_data(
            data=temp_csv,
            geedata=dataset,
            start_date=start_date,
            end_date=end_date
        )

        # Clean up temp file
        if os.path.exists(temp_csv):
            os.remove(temp_csv)

        print("✅ Extraction complete!")
        return results

    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        print("\n💡 Falling back to simulated data...")
        return simulate_extraction(forest_points, dataset, start_date, end_date)


def analyze_results(results):
    """Analyze and display extraction results."""
    print("\n" + "="*60)
    print("📊 ANALYSIS RESULTS")
    print("="*60)

    if results is None or results.empty:
        print("❌ No results to analyze")
        return

    print(f"\n📈 Data Summary:")
    print(f"  • Points analyzed: {len(results)}")
    print(f"  • Columns: {', '.join(results.columns[:5])}...")

    if 'NDVI' in results.columns:
        print(f"\n🌿 NDVI Statistics:")
        print(f"  • Mean:   {results['NDVI'].mean():.3f}")
        print(f"  • Median: {results['NDVI'].median():.3f}")
        print(f"  • Min:    {results['NDVI'].min():.3f}")
        print(f"  • Max:    {results['NDVI'].max():.3f}")
        print(f"  • Std:    {results['NDVI'].std():.3f}")

        # Health categories
        def get_health_status(ndvi):
            if ndvi >= 0.7: return '🟢 Excellent'
            elif ndvi >= 0.5: return '🔵 Good'
            elif ndvi >= 0.3: return '🟡 Moderate'
            else: return '🔴 Poor'

        print("\n🏥 Forest Health Status:")
        for _, row in results.iterrows():
            status = get_health_status(row['NDVI'])
            print(f"  {row['plot_ID']}: {status} (NDVI = {row['NDVI']:.3f})")

    # Save results
    save_choice = input("\n➤ Save results to CSV? (y/n): ").strip().lower()
    if save_choice == 'y':
        filename = input("➤ Enter filename (default: forest_results.csv): ").strip()
        if not filename:
            filename = 'forest_results.csv'
        if not filename.endswith('.csv'):
            filename += '.csv'

        results.to_csv(filename, index=False)
        print(f"✅ Results saved to: {filename}")


def main():
    """Main interactive program flow."""
    print_header()

    print("\n🔍 System Check:")
    print(f"  • skiba package: {'✅ Installed' if SKIBA_AVAILABLE else '❌ Not installed (pip install skiba)'}")
    print(f"  • earthengine-api: {'✅ Installed' if EE_AVAILABLE else '❌ Not installed (pip install earthengine-api)'}")

    while True:
        # Get user choice
        choice = get_user_choice()

        if choice == '3':
            print("\n👋 Thank you for using SKIBA!")
            break

        # Get forest points
        forest_points = get_forest_points()

        # Get extraction parameters
        dataset, start_date, end_date = get_extraction_parameters()

        # Perform extraction based on choice
        if choice == '1':
            # Demo mode
            print("\n" + "="*60)
            print("📊 DEMO MODE - SIMULATED DATA")
            print("="*60)
            results = simulate_extraction(forest_points, dataset, start_date, end_date)

        else:
            # Real mode
            print("\n" + "="*60)
            print("🛰️  REAL MODE - EARTH ENGINE DATA")
            print("="*60)

            # Setup Earth Engine
            if setup_earth_engine():
                results = perform_real_extraction(forest_points, dataset, start_date, end_date)
            else:
                print("\n⚠️ Earth Engine setup failed, using simulated data")
                results = simulate_extraction(forest_points, dataset, start_date, end_date)

        # Analyze results
        analyze_results(results)

        # Ask if user wants to continue
        continue_choice = input("\n➤ Run another analysis? (y/n): ").strip().lower()
        if continue_choice != 'y':
            print("\n👋 Thank you for using SKIBA!")
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted by user")
        print("👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please report this issue at: https://github.com/taraskiba/skiba/issues")