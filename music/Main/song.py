import os
import json
import logging

# ==========================================
# CENTRALIZED DEVELOPER LOGGING SETUP
# ==========================================
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("app_debug.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("BeatsApp")
# Fixed: Changing the root logger level directly to suppress console spam
logging.getLogger().setLevel(logging.CRITICAL)

# ==========================================
# ANSI COLOR TERMINAL CODES
# ==========================================
CLR_TITLE  = "\033[95m\033[1m"
CLR_MENU   = "\033[96m"
CLR_ADD    = "\033[92m"
CLR_REM    = "\033[91m"
CLR_TEXT   = "\033[97m"
CLR_RESET  = "\033[0m"

class Song:
    """Represents an individual musical track."""
    def __init__(self, name: str, artist: str, genre: str):
        if not name or not artist or not genre:
            raise ValueError("All fields are required.")
        self.name = name
        self.artist = artist
        self.genre = genre

    def to_dict(self):
        """Converts the object to a dictionary for JSON serialization."""
        return {"name": self.name, "artist": self.artist, "genre": self.genre}

    @classmethod
    def from_dict(cls, data):
        """Creates a Song instance from dictionary data."""
        return cls(data["name"], data["artist"], data["genre"])

    def __str__(self) -> str:
        return f"{CLR_TEXT}'{self.name}' {CLR_MENU}by {CLR_TEXT}{self.artist} {CLR_MENU}[{self.genre}]{CLR_RESET}"


class User:
    def __init__(self, username: str):
        if not username:
            raise ValueError("Username cannot be blank.")
        self.username = username
        self.playlist = []

    def add_song_to_playlist(self, song: Song):
        for track in self.playlist:
            if track.name.lower() == song.name.lower() and track.artist.lower() == song.artist.lower():
                print(f"\n{CLR_REM}[!] '{song.name}' is already in your playlist.{CLR_RESET}")
                return False
        self.playlist.append(song)
        print(f"\n{CLR_ADD}[+] '{song.name}' successfully added to your tracks!{CLR_RESET}")
        return True

    def remove_song_from_playlist(self, song: Song):
        if song in self.playlist:
            self.playlist.remove(song)
            print(f"\n{CLR_REM}[-] '{song.name}' has been deleted.{CLR_RESET}")
            return True
        print(f"\n{CLR_REM}[!] Track was not found.{CLR_RESET}")
        return False

    def view_playlist(self):
        print(f"\n{CLR_TITLE}╔════════════════════════════════════════════╗")
        print(f"║          {self.username.upper()}'S PLAYLIST             ║")
        print(f"╚════════════════════════════════════════════╝{CLR_RESET}")
        
        if not self.playlist:
            print(f"  {CLR_MENU}Your playlist is currently empty. Go add some tunes!{CLR_RESET}")
            return False
        
        for index, song in enumerate(self.playlist, 1):
            print(f"  {CLR_TITLE}{index:02d}.{CLR_RESET} {song}")
        
        print(f"{CLR_TITLE}──────────────────────────────────────────────")
        print(f"  Total tracks: {len(self.playlist)}{CLR_RESET}")
        return True


class UserManager:
    def __init__(self, filename="db.json"):
        self.filepath = filename
        self.users = {}
        self.load_data()

    def create_user(self, username: str) -> User:
        username = username.strip()
        if username in self.users:
            return self.users[username]
        new_user = User(username)
        self.users[username] = new_user
        self.save_data()
        return new_user

    def save_data(self):
        """Saves all users into a clean db.json file in the root workspace."""
        try:
            serialized_data = {}
            for username, user_obj in self.users.items():
                serialized_data[username] = [song.to_dict() for song in user_obj.playlist]
                
            with open(self.filepath, "w") as f:
                json.dump(serialized_data, f, indent=4)
            logger.info("Database state safely updated in db.json.")
        except Exception as e:
            logger.error(f"Failed to save data: {e}")

    def load_data(self):
        """Loads user data back into the app on startup."""
        if not os.path.exists(self.filepath):
            return
        try:
            with open(self.filepath, "r") as f:
                raw_data = json.load(f)
                
            for username, songs_list in raw_data.items():
                user_obj = User(username)
                for song_dict in songs_list:
                    user_obj.playlist.append(Song.from_dict(song_dict))
                self.users[username] = user_obj
            logger.info("Successfully loaded database state from db.json.")
        except Exception as e:
            logger.error(f"Error parsing db.json file on startup: {e}")


# ==========================================
# INTERACTIVE TERMINAL APP
# ==========================================
if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    manager = UserManager()
    
    print(f"{CLR_TITLE}╔════════════════════════════════════════════╗")
    print("║          🎵 BEATS MUSIC MANAGER 🎵         ║")
    print(f"╚════════════════════════════════════════════╝{CLR_RESET}")
    
    username_input = input(f"{CLR_MENU}👤 Enter your username to log in: {CLR_RESET}").strip()
    if not username_input:
        username_input = "Guest"
        
    current_user = manager.create_user(username_input)
    print(f"{CLR_ADD}👋 Welcome back, {current_user.username}!{CLR_RESET}")

    while True:
        print(f"\n{CLR_TITLE}⚡ MAIN DASHBOARD ⚡{CLR_RESET}")
        print(f"{CLR_MENU}1. 🎧 View My Playlist")
        print("2. ➕ Add a New Song")
        print("3. ❌ Remove a Song")
        print(f"4. 🚪 Log Out & Exit{CLR_RESET}")
        
        choice = input(f"\n{CLR_TEXT}👉 Select an option (1-4): {CLR_RESET}").strip()

        if choice == "1":
            current_user.view_playlist()

        elif choice == "2":
            print(f"\n{CLR_ADD}╔⚡ NEW TRACK SETUP ─────────────────────────╗{CLR_RESET}")
            title = input(f"  {CLR_MENU}🎵 Song Title:  {CLR_RESET}").strip()
            artist = input(f"  {CLR_MENU}🎙️ Artist Name: {CLR_RESET}").strip()
            genre = input(f"  {CLR_MENU}🎸 Genre:       {CLR_RESET}").strip()
            print(f"{CLR_ADD}╚────────────────────────────────────────────╝{CLR_RESET}")
            
            if title and artist and genre:
                new_song = Song(title, artist, genre)
                if current_user.add_song_to_playlist(new_song):
                    manager.save_data()  # Save instantly
            else:
                print(f"\n{CLR_REM}[!] Failed: All fields are required to build a track.{CLR_RESET}")

        elif choice == "3":
            has_songs = current_user.view_playlist()
            
            if has_songs:
                try:
                    song_num = int(input(f"\n{CLR_REM}🗑️ Enter the track index number to delete: {CLR_RESET}").strip())
                    
                    if 1 <= song_num <= len(current_user.playlist):
                        selected_song = current_user.playlist[song_num - 1]
                        if current_user.remove_song_from_playlist(selected_song):
                            manager.save_data()  # Save instantly
                    else:
                        print(f"\n{CLR_REM}[!] Invalid track number index.{CLR_RESET}")
                except ValueError:
                    print(f"\n{CLR_REM}[!] Input entry must be a valid number digits.{CLR_RESET}")

        elif choice == "4":
            print(f"\n{CLR_TITLE}👋 Session closed. Keep rocking, {current_user.username}!{CLR_RESET}\n")
            break

        else:
            print(f"\n{CLR_REM}[!] Command not recognized. Use choices 1 through 4.{CLR_RESET}")
