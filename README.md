# Music Playlist Manager

## Purpose

This project is a simple terminal-based music playlist manager written in Python. It allows users to create a username, add songs to a personal playlist, remove songs, and view their current playlist. User data is persisted in `db.json` so the playlist is saved between runs.

## Requirements

- Python 3.10 or higher
- `pytest` for running the test suite

## Installation

1. Ensure Python 3.10+ is installed.
2. Install the test dependency:
   ```bash
   pip install pytest
   ```

## Usage

Run the application with:

```bash
python music/Main/song.py
```

## Testing

Run the tests from the project root with:

```bash
PYTHONPATH=. pytest music/Testing/test_song.py -v
```
