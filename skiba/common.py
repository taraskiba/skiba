"""The common module contains common functions and classes used by the other modules."""

import pandas as pd
from datetime import date
from typing import Union, Optional


def hello_world():
    """Prints "Hello World!" to the console."""
    print("Hello World!")


def validate_coordinates(
    df: pd.DataFrame, lat_col: str = "LAT", lon_col: str = "LON"
) -> list[str]:
    """
    Validate coordinate data and return list of errors.

    Args:
        df: DataFrame containing coordinate columns
        lat_col: Name of latitude column
        lon_col: Name of longitude column

    Returns:
        List of error messages (empty if validation passes)
    """
    errors = []

    # Check if columns exist
    if lat_col not in df.columns:
        errors.append(f"Latitude column '{lat_col}' not found in data")
        return errors
    if lon_col not in df.columns:
        errors.append(f"Longitude column '{lon_col}' not found in data")
        return errors

    # Check for missing values
    if df[lat_col].isna().any():
        na_count = df[lat_col].isna().sum()
        errors.append(f"Latitude column contains {na_count} missing value(s)")
    if df[lon_col].isna().any():
        na_count = df[lon_col].isna().sum()
        errors.append(f"Longitude column contains {na_count} missing value(s)")

    # Check latitude bounds (-90 to 90)
    lat_min = df[lat_col].min()
    lat_max = df[lat_col].max()
    if lat_min < -90 or lat_max > 90:
        errors.append(
            f"Latitude values must be between -90 and 90. Found range: [{lat_min}, {lat_max}]"
        )

    # Check longitude bounds (-180 to 180)
    lon_min = df[lon_col].min()
    lon_max = df[lon_col].max()
    if lon_min < -180 or lon_max > 180:
        errors.append(
            f"Longitude values must be between -180 and 180. Found range: [{lon_min}, {lon_max}]"
        )

    return errors


def validate_date_range(
    start_date: Optional[Union[date, str]], end_date: Optional[Union[date, str]]
) -> list[str]:
    """
    Validate date range parameters.

    Args:
        start_date: Start date (date object or string in YYYY-MM-DD format)
        end_date: End date (date object or string in YYYY-MM-DD format)

    Returns:
        List of error messages (empty if validation passes)
    """
    errors = []

    # If both are None, that's valid (no date filtering)
    if start_date is None and end_date is None:
        return errors

    # If only one is provided, that's an error
    if start_date is None and end_date is not None:
        errors.append("Start date is required when end date is provided")
        return errors
    if end_date is None and start_date is not None:
        errors.append("End date is required when start date is provided")
        return errors

    # Convert strings to date objects if needed
    try:
        if isinstance(start_date, str):
            from datetime import datetime

            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        if isinstance(end_date, str):
            from datetime import datetime

            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError as e:
        errors.append(f"Invalid date format. Use YYYY-MM-DD format. Error: {e}")
        return errors

    # Check that start_date is before end_date
    if start_date > end_date:
        errors.append(
            f"Start date ({start_date}) must be before or equal to end date ({end_date})"
        )

    return errors


def validate_buffer_radius(radius: float) -> list[str]:
    """
    Validate buffer radius parameter.

    Args:
        radius: Buffer radius in feet

    Returns:
        List of error messages (empty if validation passes)
    """
    errors = []

    # Check for valid type
    if not isinstance(radius, (int, float)):
        errors.append(f"Buffer radius must be a number, got {type(radius).__name__}")
        return errors

    # Check for positive value
    if radius <= 0:
        errors.append(f"Buffer radius must be positive, got {radius}")

    # Warn about excessively large radius (> 1 mile = 5280 feet)
    if radius > 5280:
        errors.append(
            f"Buffer radius of {radius} feet exceeds 1 mile. "
            "This may result in very large areas and slow processing."
        )

    return errors


def validate_sample_count(count: int) -> list[str]:
    """
    Validate sample count parameter.

    Args:
        count: Number of sample points to generate

    Returns:
        List of error messages (empty if validation passes)
    """
    errors = []

    # Check for valid type
    if not isinstance(count, int):
        errors.append(f"Sample count must be an integer, got {type(count).__name__}")
        return errors

    # Check for positive value
    if count <= 0:
        errors.append(f"Sample count must be positive, got {count}")

    # Warn about large sample counts
    if count > 100:
        errors.append(
            f"Sample count of {count} is large. "
            "This may result in slow processing and large output files."
        )

    return errors
