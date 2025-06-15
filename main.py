
import pyfiglet
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup
import requests

# load .env
load_dotenv()
spotify_client_id = os.getenv("SPOTIFY_CLIENT_ID")
spotify_client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
spotify_redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")

# ascii art and user input 
print(pyfiglet.figlet_format("\n Musically Time Machine \n\n"))
date = input("What is your Date of Birth? Type the date in this format YYYY-MM-DD: ")

# Separate 100 song titles from Billboard on particular date
header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"}
url = "https://www.billboard.com/charts/hot-100/" + date

response = requests.get(url, headers=header)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

songs_name = [song.getText().strip() for song in soup.select("li ul li h3")]

# Spotify Authentication
scope = "playlist-modify-private user-library-read user-read-private"
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope=scope, 
        redirect_uri=spotify_redirect_uri, 
        client_id=spotify_client_id, 
        client_secret=spotify_client_secret, 
        show_dialog=True, 
        cache_path="token.txt", 
        username="mdf8wq20vlbp7ls4mbowpei9j"
        )
    )

# First get current user (requires user-read-private scope)
user = sp.current_user()
user_id = user["id"]
print(f"Authenticated as user: {user['display_name']}")

# Now access saved tracks 
try:
    results = sp.current_user_saved_tracks(limit=5)  # Start with small limit for testing
    for idx, item in enumerate(results['items']):
        track = item['track']
        print(f"{idx + 1}. {track['artists'][0]['name']} – {track['name']}")
except spotipy.SpotifyException as e:
    print(f"Error accessing saved tracks: {e}")

# Search for songs
song_uris = []
added_songs = 0
skipped_songs = 0
year = date.split("-")[0]
for song in songs_name:
    result = sp.search(q=f"track:{song} year:{year}", type="track")
    try:
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
        # print(f"{song} added to Spotify playlist.")
        added_songs += 1
    except IndexError:
        # print(f"{song} doesn't exist in Spotify. Skipped.")
        skipped_songs += 1

print(f"Number of Songs Available: {added_songs}")
print(f"Number of Songs Not Available: {skipped_songs}")

# Create playlist
playlist = sp.user_playlist_create(user=user_id, name=f"{date} Billboard 100", public=False)
sp.playlist_add_items(playlist_id=playlist["id"], items=song_uris)
print(f"Playlist '{playlist['name']}' created successfully!\nWe've managed to add {len(song_uris)}/100 songs to it. Enjoy!")


