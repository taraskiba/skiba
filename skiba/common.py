"""The common module contains common functions and classes used by the other modules."""


def hello_world():
    """Prints "Hello World!" to the console."""
    print("Hello World!")


def to_utm_crs(point):
    """Return the EPSG code of the UTM zone that contains the given point.

    Hemisphere-aware (326xx north, 327xx south) and zero-pads zones 1-9
    so pyproj receives a valid 5-digit EPSG code.

    Args:
        point: A shapely Point in EPSG:4326 (lon=x, lat=y).

    Returns:
        str: EPSG code like ``"EPSG:32610"`` or ``"EPSG:32705"``.

    Raises:
        ValueError: If the point is outside the standard UTM latitude band
            (|lat| > 84); UPS would be required there.
    """
    lon, lat = point.x, point.y
    if lat > 84 or lat < -80:
        raise ValueError(
            f"Point at lat={lat} is outside the standard UTM band (-80, 84); "
            "use UPS for polar regions."
        )
    zone = int((lon + 180) // 6) + 1
    # Antimeridian edge case: lon == 180 yields zone 61; clamp to 60.
    zone = min(zone, 60)
    hemisphere_prefix = 326 if lat >= 0 else 327
    return f"EPSG:{hemisphere_prefix}{zone:02d}"
