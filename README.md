# py-gtfs-loader

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://github.com/TransitApp/py-gtfs-loader/workflows/Build%20on%20pull%20request/badge.svg)](https://github.com/TransitApp/py-gtfs-loader/actions)

A Python library for loading and manipulating GTFS (General Transit Feed Specification) data with schema validation and type safety.

## Features

- 📦 Load GTFS feeds from directories
- ✅ Schema validation with type checking
- 🔄 Modify and patch GTFS data
- 🚀 Support for standard GTFS and Transit's itinerary format
- 📝 CSV and GeoJSON file type support
- 🔗 Cross-referenced entities for easy data navigation

## Installation

```bash
pip install py-gtfs-loader
```

Or using uv:

```bash
uv add py-gtfs-loader
```

## Quick Start

### Loading GTFS Data

```python
import gtfs_loader

# Load a GTFS feed
gtfs = gtfs_loader.load('path/to/gtfs/directory')

# Access data by entity
stop = gtfs.stops['stop_id']
route = gtfs.routes['route_id']
trip = gtfs.trips['trip_id']

# Access grouped entities
stop_times = gtfs.stop_times['trip_id']  # Returns list of stop times for a trip
```

### Modifying and Saving GTFS Data

```python
# Modify data
gtfs.stops['stop_id'].stop_name = "New Stop Name"

# Save changes back to disk
gtfs_loader.patch(gtfs, 'path/to/input', 'path/to/output')
```

### Loading Specific Files

```python
# Load only specific files
gtfs = gtfs_loader.load('path/to/gtfs', files=['stops', 'routes', 'trips'])
```

### Transit Itinerary Format

```python
# Load Transit itinerary format (itinerary_cells.txt)
gtfs = gtfs_loader.load('path/to/gtfs', itineraries=True)
```

## Development

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

### Setup

```bash
# Install dependencies
uv sync --all-extras --dev

# Run tests
uv run pytest .

# Run linting
uv run flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
```

### Requirements

- Python ≥ 3.10
- Development dependencies: pytest, flake8

## Project Structure

- `gtfs_loader/` - Main package
  - `__init__.py` - Load/patch functions
  - `schema.py` - GTFS entity definitions
  - `schema_classes.py` - Schema metadata system
  - `types.py` - Custom GTFS types (GTFSTime, GTFSDate, Entity)
  - `lat_lon.py` - Geographic utilities

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details

## Maintainers

- Jonathan Milot
- Jeremy Steele