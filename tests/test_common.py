#!/usr/bin/env python

"""Tests for common module."""

import unittest
from unittest.mock import patch
from io import StringIO

from shapely.geometry import Point

from skiba.common import hello_world, to_utm_crs


class TestCommon(unittest.TestCase):
    """Tests for common module functions."""

    def test_hello_world_prints_correct_message(self):
        """Test that hello_world prints 'Hello World!' to stdout."""
        with patch("sys.stdout", new=StringIO()) as fake_output:
            hello_world()
            self.assertEqual(fake_output.getvalue().strip(), "Hello World!")

    def test_hello_world_returns_none(self):
        """Test that hello_world returns None."""
        with patch("sys.stdout", new=StringIO()):
            result = hello_world()
            self.assertIsNone(result)


class TestToUtmCrs(unittest.TestCase):
    """Tests for hemisphere-aware UTM zone construction (issue #87)."""

    def test_northern_hemisphere_two_digit_zone(self):
        # San Francisco, CA: zone 10N
        self.assertEqual(to_utm_crs(Point(-122.4194, 37.7749)), "EPSG:32610")

    def test_northern_hemisphere_single_digit_zone_is_zero_padded(self):
        # lon=-153 → zone 5N (Aleutian Islands region).
        # Previous buggy code produced "EPSG:3265" (wrong CRS entirely).
        self.assertEqual(to_utm_crs(Point(-153.0, 57.0)), "EPSG:32605")

    def test_southern_hemisphere_uses_327_prefix(self):
        # Buenos Aires: zone 21S.
        # Previous buggy code produced "EPSG:32621" (North zone) silently.
        self.assertEqual(to_utm_crs(Point(-58.3816, -34.6037)), "EPSG:32721")

    def test_southern_hemisphere_single_digit_zone(self):
        # lon=-153 in the Southern Pacific → zone 5S.
        self.assertEqual(to_utm_crs(Point(-153.0, -20.0)), "EPSG:32705")

    def test_equator_treated_as_northern(self):
        # lat == 0 uses the northern prefix by convention.
        self.assertEqual(to_utm_crs(Point(0.0, 0.0)), "EPSG:32631")

    def test_antimeridian_clamps_to_zone_60(self):
        # lon == 180 would naively produce zone 61; must clamp to 60.
        self.assertEqual(to_utm_crs(Point(180.0, 0.0)), "EPSG:32660")

    def test_raises_outside_utm_band(self):
        with self.assertRaises(ValueError):
            to_utm_crs(Point(0.0, 85.0))
        with self.assertRaises(ValueError):
            to_utm_crs(Point(0.0, -85.0))


if __name__ == "__main__":
    unittest.main()
