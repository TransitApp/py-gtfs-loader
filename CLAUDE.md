# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

py-gtfs-loader is a Python library for loading and manipulating GTFS (General Transit Feed Specification) data. It parses GTFS directories into Python objects with schema validation and provides utilities for reading, modifying, and writing GTFS feeds.

## Development Commands

### Using uv (package manager)

```bash
# Install dependencies
uv sync --all-extras --dev

# Run tests
uv run pytest .

# Run linting
uv run flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
uv run flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

# Build package
uv build

# Run a single test file
uv run pytest tests/test_runner.py

# Run a specific test case
uv run pytest tests/test_runner.py::test_default -k "test_name"
```

## Architecture

### Core Components

**`gtfs_loader/__init__.py`** - Main entry point with load/patch functions
- `load(gtfs_dir, ...)`: Parses GTFS directory into structured objects
- `patch(gtfs, gtfs_in_dir, gtfs_out_dir, ...)`: Modifies and writes GTFS data back to disk
- Supports both standard GTFS and Transit itinerary format via `itineraries=True` flag
- CSV and GeoJSON file type support

**`gtfs_loader/schema.py`** - GTFS entity definitions and schemas
- Defines all GTFS entities (Agency, Route, Trip, Stop, StopTime, etc.)
- Entity classes have `_schema` attribute describing file structure (ID, grouping, required fields)
- Two schema collections: `GTFS_SUBSET_SCHEMA` (standard) and `GTFS_SUBSET_SCHEMA_ITINERARIES` (Transit format)
- Entities reference other entities via `_gtfs` attribute (e.g., `stop_time.stop` resolves to Stop object)

**`gtfs_loader/schema_classes.py`** - Schema metadata system
- `File`: Describes GTFS file structure (primary key, grouping, file type)
- `Field`: Named tuple for field configuration (type, required, default)
- `FileCollection`: Container for file schemas
- Grouping support: entities with same ID can be grouped by secondary key (e.g., stop_times grouped by trip_id + stop_sequence)

**`gtfs_loader/types.py`** - Custom types and base classes
- `GTFSTime`: Integer-based time allowing >24h (e.g., "25:30:00" for next-day services)
- `GTFSDate`: datetime subclass parsing YYYYMMDD and YYYY-MM-DD formats
- `Entity`: Base class for all GTFS entities, dict-like with `_gtfs` reference to parent collection
- `EntityDict`: Dict subclass storing resolved field metadata

### Data Flow

1. **Load**: CSV/GeoJSON → parse headers → validate fields → create Entity objects → index by ID → return nested dict structure
2. **Access**: `gtfs.stops['stop_id']` or `gtfs.stop_times['trip_id'][sequence_index]`
3. **Patch**: Flatten nested structures → write CSV with correct headers → preserve unmodified files

### Key Patterns

- **Entity indexing**: Primary entities indexed by `id` field, grouped entities create nested dicts/lists
- **Cross-references**: Entities access related data via `_gtfs` backref (e.g., `trip.route`, `stop_time.stop`)
- **Computed properties**: Use `@cached_property` for derived values (e.g., `trip.first_departure`)
- **Two GTFS formats**: Standard (stop_times.txt) vs Transit itinerary format (itinerary_cells.txt + trip arrays)

## Itinerary Format Support

The library supports Transit's custom itinerary format where:
- `itinerary_cells.txt` defines stop sequences (like templates)
- Trips reference itineraries and contain time arrays instead of individual stop_times
- Use `itineraries=True` flag when loading/patching to use this format
