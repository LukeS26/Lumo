import spotdl
from spotdl.utils.config import create_settings
import json
import os
from config.config_variables import api_credentials
import re

playlist_url = "https://open.spotify.com/playlist/507kNWtpKm3BBnmKKR4CCR?si=301a7be884f54582"
client = spotdl.Spotdl(api_credentials["spotify"]["client_id"], api_credentials["spotify"]["client_secret"])

def clean_filename(filename):
    invalid_chars = r'[<>:"/\\|?*]'
    cleaned_filename = re.sub(invalid_chars, '', filename)
    return cleaned_filename

artists = json.load(open("./music/artists.json"))
songs = json.load(open("./music/songs.json"))

song_list = {}

for artist in artists:
    song_list[artists[artist]["name"]] = []
    for song in artists[artist]["songs"]:
        song_list[artists[artist]["name"]].append(songs[song]["name"])


songs = client.search([playlist_url])

songs_to_download = []

print("Searched")

for song in songs:
    #Already downloaded song, so skip re-downloading it
    if song.artist in song_list.keys() and song.name in song_list[song.artist]:
        continue

    songs_to_download.append(song)
    

downloaded_songs = client.download_songs(songs_to_download)

for (song, path) in downloaded_songs:
    if not song.artist in os.listdir("./music/music_library"):
        try:
            os.mkdir(f"./music/music_library/{clean_filename(song.artist)}")
        except Exception as e:
            print(e)

    if not song.album_name in os.listdir(f"./music/music_library/{song.artist}"):
        try:
            os.mkdir(f"./music/music_library/{clean_filename(song.artist)}/{clean_filename(song.album_name)}")
        except Exception as e:
            print(e)
    try:
        os.rename(path, f"./music/music_library/{clean_filename(song.artist)}/{clean_filename(song.album_name)}/{clean_filename(song.name)}.mp3")
    except Exception as e:
        print(e)

    try:
        os.remove(path)
    except Exception as e:
        print(e)