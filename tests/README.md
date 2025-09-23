# Skiba Test Suite

This directory contains the comprehensive test suite for the skiba package.

## Running Tests

### Install test dependencies
```bash
pip install -e ".[dev]"
# or
pip install pytest pytest-cov pytest-mock requests-mock
```

### Run all tests
```bash
pytest
```

### Run with coverage report
```bash
pytest --cov=skiba --cov-report=term-missing
```

### Run specific test file
```bash
pytest tests/test_common.py
```

### Run tests with verbose output
```bash
pytest -v
```

## Test Structure

- `test_common.py` - Tests for utility functions in common.py
- `test_point_extraction.py` - Tests for point extraction functionality
- `test_buffer_coordinates.py` - Tests for coordinate buffering operations
- `test_area_extraction.py` - Tests for area-based data extraction (TODO)
- `test_buffer_and_sample.py` - Tests for buffer and sampling operations (TODO)
- `test_geojson_buffering.py` - Tests for GeoJSON buffering (TODO)

## Coverage Goals

We aim for at least 80% code coverage across all modules.

## Writing Tests

When adding new features or fixing bugs, please ensure:
1. Write tests before implementing the feature (TDD approach)
2. Test both success and failure cases
3. Mock external dependencies (APIs, file I/O, etc.)
4. Keep tests focused and independent
5. Use descriptive test names that explain what is being tested

## Mocking Guidelines

- Mock all external API calls (Google Earth Engine, web requests)
- Mock file I/O operations when testing logic
- Mock GUI widgets (ipywidgets) to test business logic
- Use `pytest-mock` and `requests-mock` for consistent mocking