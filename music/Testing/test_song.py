import os
import json
import pytest
from music.Main.song import Song, User, UserManager

# =====================================================================
# FIXTURES (Setup helpers for isolated testing environment)
# =====================================================================

@pytest.fixture
def temp_db(tmp_path):
    """Creates a temporary isolated json file location for testing databases."""
    db_file = tmp_path / "test_db.json"
    return str(db_file)

@pytest.fixture
def manager(temp_db):
    """Provides a fresh UserManager pointing to our temp database file."""
    return UserManager(filename=temp_db)

@pytest.fixture
def sample_song():
    """Provides a valid test song instance."""
    return Song("Blinding Lights", "The Weeknd", "Pop")


# =====================================================================
# 1. CORE LOGIC UNIT TESTS (Song, User & Manager)
# =====================================================================

def test_song_initialization_valid(sample_song):
    """Verifies that properties are correctly mapped in Song objects."""
    assert sample_song.name == "Blinding Lights"
    assert sample_song.artist == "The Weeknd"
    assert sample_song.genre == "Pop"

def test_song_initialization_invalid():
    """Confirms system correctly catches validation errors for blank arguments."""
    with pytest.raises(ValueError, match="All fields are required."):
        Song("", "The Weeknd", "Pop")

def test_user_initialization_valid():
    """Verifies user profile starts with an empty playlist track collection."""
    user = User("Alice")
    assert user.username == "Alice"
    assert len(user.playlist) == 0

def test_user_initialization_invalid():
    """Ensures profile generator blocks blank username initialization requests."""
    with pytest.raises(ValueError, match="Username cannot be blank."):
        User("")

def test_add_song_to_playlist(manager, sample_song):
    """Verifies new songs correctly append inside a profile's tracker list."""
    user = manager.create_user("Alice")
    success = user.add_song_to_playlist(sample_song)
    
    assert success is True
    assert len(user.playlist) == 1
    assert user.playlist[0].name == "Blinding Lights"

def test_add_duplicate_song_prevention(manager, sample_song):
    """Ensures duplicate songs are safely caught and ignored."""
    user = manager.create_user("Alice")
    user.add_song_to_playlist(sample_song)
    
    # Attempting to add the identical track object state again
    duplicate_success = user.add_song_to_playlist(sample_song)
    assert duplicate_success is False
    assert len(user.playlist) == 1

def test_remove_song_from_playlist(manager, sample_song):
    """Ensures removal code safely handles removing tracks out of playlists."""
    user = manager.create_user("Alice")
    user.add_song_to_playlist(sample_song)
    
    success = user.remove_song_from_playlist(sample_song)
    assert success is True
    assert len(user.playlist) == 0

def test_remove_non_existent_song(manager, sample_song):
    """Confirms system handles requests to delete non-existent tracks gracefully."""
    user = manager.create_user("Alice")
    success = user.remove_song_from_playlist(sample_song)
    assert success is False


# =====================================================================
# 2. FILE PERSISTENCE & DB TESTS
# =====================================================================

def test_database_save_and_load(temp_db, sample_song):
    """Verifies data safely transfers to the db.json file and persists correctly."""
    # 1. Create a session to save data
    manager1 = UserManager(filename=temp_db)
    user1 = manager1.create_user("Bob")
    user1.add_song_to_playlist(sample_song)
    manager1.save_data()
    
    # Check if file was physically generated on disk drive path
    assert os.path.exists(temp_db) is True
    
    # Verify file contents are valid JSON format structural maps
    with open(temp_db, "r") as f:
        file_contents = json.load(f)
        assert "Bob" in file_contents
        assert file_contents["Bob"][0]["name"] == "Blinding Lights"

    # 2. Spin up a separate manager session to read data back into memory structure
    manager2 = UserManager(filename=temp_db)
    assert "Bob" in manager2.users
    assert len(manager2.users["Bob"].playlist) == 1
    assert manager2.users["Bob"].playlist[0].artist == "The Weeknd"


# =====================================================================
# 3. INTERACTIVE CLI BEHAVIOR MOCKING TESTS
# =====================================================================

def test_cli_view_playlist_empty_vs_populated(manager, sample_song, capsys):
    """Uses pytest capsys to intercept print statements to ensure views map properly."""
    user = manager.create_user("Charlie")
    
    # Check empty view state output returns matching string conditions
    empty_result = user.view_playlist()
    assert empty_result is False
    captured = capsys.readouterr()
    assert "playlist is currently empty" in captured.out

    # Check populated track collection prints tracks output items text indexes
    user.add_song_to_playlist(sample_song)
    populated_result = user.view_playlist()
    assert populated_result is True
    captured = capsys.readouterr()
    assert "CHARLIE'S PLAYLIST" in captured.out
    assert "Blinding Lights" in captured.out
