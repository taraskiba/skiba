#!/usr/bin/env python

"""Tests for common module."""

import unittest
from unittest.mock import patch
from io import StringIO

from skiba.common import hello_world


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


if __name__ == "__main__":
    unittest.main()
