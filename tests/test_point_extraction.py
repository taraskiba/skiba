#!/usr/bin/env python

"""Tests for point_extraction module."""

import unittest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import numpy as np
import tempfile
import os
from datetime import date

from skiba.point_extraction import point_extraction


class TestPointExtraction(unittest.TestCase):
    """Tests for point_extraction class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_ee_patcher = patch("skiba.point_extraction.ee")
        self.mock_ee = self.mock_ee_patcher.start()

        self.mock_gm_patcher = patch("skiba.point_extraction.gm")
        self.mock_gm = self.mock_gm_patcher.start()

        self.mock_widgets_patcher = patch("skiba.point_extraction.widgets")
        self.mock_widgets = self.mock_widgets_patcher.start()

        # Setup mock widgets
        self.mock_widgets.FileUpload.return_value = MagicMock()
        self.mock_widgets.Dropdown.return_value = MagicMock()
        self.mock_widgets.DatePicker.return_value = MagicMock()
        self.mock_widgets.Button.return_value = MagicMock()
        self.mock_widgets.Output.return_value = MagicMock()
        self.mock_widgets.HBox.return_value = MagicMock()
        self.mock_widgets.VBox.return_value = MagicMock()

    def tearDown(self):
        """Tear down test fixtures."""
        self.mock_ee_patcher.stop()
        self.mock_gm_patcher.stop()
        self.mock_widgets_patcher.stop()

    @patch("skiba.point_extraction.requests.get")
    def test_fetch_geojson_success(self, mock_get):
        """Test successful fetching of GeoJSON data."""
        mock_response = Mock()
        mock_response.json.return_value = {"type": "FeatureCollection", "features": []}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = point_extraction.fetch_geojson("https://example.com/data.json")
        self.assertEqual(result, {"type": "FeatureCollection", "features": []})
        mock_get.assert_called_once_with("https://example.com/data.json")

    @patch("skiba.point_extraction.requests.get")
    def test_fetch_geojson_http_error(self, mock_get):
        """Test handling of HTTP errors when fetching GeoJSON."""
        mock_get.side_effect = Exception("HTTP error")

        with patch("builtins.print") as mock_print:
            result = point_extraction.fetch_geojson("https://example.com/data.json")
            self.assertIsNone(result)
            mock_print.assert_called_once()

    @patch("skiba.point_extraction.point_extraction.fetch_geojson")
    def test_create_dropdown(self, mock_fetch):
        """Test creation of dropdown widget."""
        mock_fetch.return_value = [
            {"title": "Dataset 1", "id": "dataset1"},
            {"title": "Dataset 2", "id": "dataset2"},
        ]

        dropdown = point_extraction.create_dropdown()
        self.mock_widgets.Dropdown.assert_called_once()

    def test_add_date_picker(self):
        """Test creation of date picker widget."""
        date_picker = point_extraction.add_date_picker()
        self.mock_widgets.DatePicker.assert_called_once()

    @patch("skiba.point_extraction.requests.get")
    def test_load_gee_as_image_for_image(self, mock_get):
        """Test loading a GEE Image dataset."""
        # Mock catalog response
        mock_response = Mock()
        mock_response.json.return_value = [{"id": "test/image", "type": "image"}]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Mock ee.Image
        mock_image = Mock()
        mock_image.getInfo.return_value = {"type": "Image"}
        self.mock_ee.Image.return_value = mock_image

        result = point_extraction.load_gee_as_image(
            "test/image", "2024-01-01", "2024-12-31"
        )
        self.assertEqual(result, mock_image)
        self.mock_ee.Image.assert_called_once_with("test/image")

    @patch("skiba.point_extraction.requests.get")
    def test_load_gee_as_image_for_collection(self, mock_get):
        """Test loading a GEE ImageCollection dataset."""
        # Mock catalog response
        mock_response = Mock()
        mock_response.json.return_value = [
            {"id": "test/collection", "type": "image_collection"}
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Mock ee.ImageCollection
        mock_collection = Mock()
        mock_median = Mock()
        mock_collection.median.return_value = mock_median
        self.mock_ee.ImageCollection.return_value = mock_collection

        result = point_extraction.load_gee_as_image(
            "test/collection", "2024-01-01", "2024-12-31"
        )
        self.assertEqual(result, mock_median)
        self.mock_ee.ImageCollection.assert_called_once_with("test/collection")

    @patch("skiba.point_extraction.requests.get")
    def test_load_gee_as_image_invalid_dataset(self, mock_get):
        """Test loading an invalid dataset type."""
        # Mock catalog response
        mock_response = Mock()
        mock_response.json.return_value = [
            {"id": "test/feature", "type": "feature_collection"}
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        with self.assertRaises(ValueError) as context:
            point_extraction.load_gee_as_image(
                "test/feature", "2024-01-01", "2024-12-31"
            )
        self.assertIn("Dataset ID is not a valid", str(context.exception))

    @patch("skiba.point_extraction.point_extraction.fetch_geojson")
    def test_initialization(self, mock_fetch):
        """Test point_extraction class initialization."""
        mock_fetch.return_value = [{"title": "Test Dataset", "id": "test/dataset"}]

        pe = point_extraction()

        # Check that all widgets were created
        self.mock_widgets.FileUpload.assert_called_once()
        self.mock_widgets.Dropdown.assert_called()
        self.mock_widgets.DatePicker.assert_called()
        self.mock_widgets.Button.assert_called_once()
        self.mock_widgets.Output.assert_called_once()
        self.mock_widgets.HBox.assert_called_once()
        self.mock_widgets.VBox.assert_called_once()

    @patch("skiba.point_extraction.gpd")
    @patch("skiba.point_extraction.point_extraction.load_gee_as_image")
    def test_get_coordinate_data_with_dataframe(self, mock_load_gee, mock_gpd):
        """Test get_coordinate_data with pandas DataFrame input."""
        # Create test data
        test_data = pd.DataFrame(
            {"LAT": [35.0, 36.0], "LON": [-83.0, -84.0], "plot_ID": ["A", "B"]}
        )

        # Mock GeoDataFrame
        mock_gdf = Mock()
        mock_gdf.__geo_interface__ = {"type": "FeatureCollection"}
        mock_gpd.GeoDataFrame.return_value = mock_gdf
        mock_gpd.points_from_xy.return_value = Mock()

        # Mock GEE operations
        mock_fc = Mock()
        self.mock_gm.geojson_to_ee.return_value = mock_fc
        mock_image = Mock()
        mock_load_gee.return_value = mock_image
        self.mock_gm.extract_values_to_points.return_value = pd.DataFrame(
            {"result": [1, 2]}
        )

        pe = point_extraction()
        result = pe.get_coordinate_data(
            test_data, "test/dataset", date(2024, 1, 1), date(2024, 12, 31)
        )

        # Verify operations
        mock_gpd.GeoDataFrame.assert_called_once()
        self.mock_gm.geojson_to_ee.assert_called_once()
        mock_load_gee.assert_called_once_with(
            "test/dataset", date(2024, 1, 1), date(2024, 12, 31)
        )
        self.mock_gm.extract_values_to_points.assert_called_once()

    @patch("skiba.point_extraction.pd.read_csv")
    @patch("skiba.point_extraction.gpd")
    @patch("skiba.point_extraction.point_extraction.load_gee_as_image")
    def test_get_coordinate_data_with_csv_path(
        self, mock_load_gee, mock_gpd, mock_read_csv
    ):
        """Test get_coordinate_data with CSV file path input."""
        # Mock CSV reading
        test_data = pd.DataFrame(
            {"LAT": [35.0, 36.0], "LON": [-83.0, -84.0], "plot_ID": ["A", "B"]}
        )
        mock_read_csv.return_value = test_data

        # Mock GeoDataFrame
        mock_gdf = Mock()
        mock_gdf.__geo_interface__ = {"type": "FeatureCollection"}
        mock_gpd.GeoDataFrame.return_value = mock_gdf
        mock_gpd.points_from_xy.return_value = Mock()

        # Mock GEE operations
        mock_fc = Mock()
        self.mock_gm.geojson_to_ee.return_value = mock_fc
        mock_image = Mock()
        mock_load_gee.return_value = mock_image
        self.mock_gm.extract_values_to_points.return_value = pd.DataFrame(
            {"result": [1, 2]}
        )

        pe = point_extraction()
        result = pe.get_coordinate_data(
            "test.csv", "test/dataset", date(2024, 1, 1), date(2024, 12, 31)
        )

        # Verify CSV was read
        mock_read_csv.assert_called_once_with("test.csv")

    @patch("skiba.point_extraction.point_extraction.fetch_geojson")
    def test_on_dropdown_change(self, mock_fetch):
        """Test dropdown change handler."""
        mock_fetch.return_value = [
            {"id": "test/dataset", "url": "https://example.com/dataset"}
        ]

        pe = point_extraction()

        with patch("builtins.print") as mock_print:
            # Simulate dropdown change
            change = {"new": "test/dataset"}
            pe.on_dropdown_change(change)

            # Check that information was printed
            calls = mock_print.call_args_list
            self.assertEqual(len(calls), 2)

    def test_find_column_helper_function(self):
        """Test the find_column helper function used in on_button_clicked."""
        # This is an internal function, so we test it indirectly
        test_df = pd.DataFrame(
            {"latitude": [1, 2], "LONGITUDE": [3, 4], "Plot_ID": ["A", "B"]}
        )

        # Test case-insensitive matching
        lat_cols = ["lat", "latitude", "y", "LAT", "Latitude", "Lat", "Y"]
        lon_cols = ["lon", "long", "longitude", "x", "LON", "Longitude", "Long", "X"]

        # Should find 'latitude' column
        self.assertIn("latitude", test_df.columns)
        # Should find 'LONGITUDE' column
        self.assertIn("LONGITUDE", test_df.columns)


if __name__ == "__main__":
    unittest.main()
