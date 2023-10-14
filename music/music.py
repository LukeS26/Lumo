import threading
import subprocess
import json
import psutil
import random
import re
import openai
import os
import time
import whisper_timestamped as whisper

from config.config_variables import api_credentials

openai.api_key = api_credentials["openai"]["key"]

class MusicController:
    def __init__(self):
        # The psutil process running ffplay
        self.music_player = None
        
        self.player_lock = False

        # The current song being played, as its id
        self.current_song = 0
       
        # The current lyric of the song playing
        self.lyric_index = 0
        
        # Variables for playback time calculation
        self.pause_time = 0
        self.paused_at = 0
        self.seek_start = 0

        # The dicts of artists, albums, and songs
        self.artists = json.load(open("./music/artists.json"))
        self.albums = json.load(open("./music/albums.json"))
        self.songs = json.load(open("./music/songs.json"))

        self.used_songs = []
        self.played_list = []
        self.available_songs = []

    # Gets the current playback time through the song. 
    # To do so it takes the current time since the creation of the music player, and subtracts the amount of time it has been paused
    # If the music is paused, then it uses the time it was paused at, instead of the current time, since in that case it won't be playing
    def get_play_time(self):
        if self.music_player is None:
            return 0

        if self.is_paused():
            return (self.paused_at - self.music_player.create_time()) - self.pause_time + self.seek_start
        else:
            return (time.time() - self.music_player.create_time()) - self.pause_time + self.seek_start

    def is_paused(self):
        try:
            return self.music_player is None or self.music_player.status() != "running"
        except psutil.NoSuchProcess:
            return True
    
    def get_current_song(self):
        return self.played_list[self.current_song]

    def pause(self):
        self.paused_at = time.time()
        self.music_player.suspend()
                
    def unpause(self):
        self.pause_time += time.time() - self.paused_at
        self.music_player.resume()

    def skip_songs(self, num):
        self.current_song = self.get_next_song(num)
        
        self.music_player.kill()
        self.music_player = None

    def seek(self, seconds):
        if self.player_lock:
            return

        self.player_lock = True

        self.pause_time = 0
    
        self.seek_start = min(max(0, self.get_play_time() + seconds), float(self.songs[self.get_current_song()]["duration"]))

        self.lyric_index = 0

        self.music_player.kill()

        args = ["ffplay", "-autoexit", "-nodisp", "-ss", str(self.seek_start), self.songs[self.get_current_song()]["link"]]
        self.music_player = psutil.Process(subprocess.Popen(
            args=args,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE
        ).pid)

    def play(self):
        if not (self.music_player is None):
            self.current_song = self.get_next_song(1)

            if self.music_player.is_running():
                self.music_player.kill()
        
        self.pause_time = 0
        self.seek_start = 0
        self.lyric_index = 0

        args = ["ffplay", "-autoexit", "-nodisp", self.songs[self.get_current_song()]["link"]]
        self.music_player = psutil.Process(subprocess.Popen(
            args=args,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE
        ).pid)

        print(f"Now playing {self.songs[self.get_current_song()]['name']} by {self.songs[self.get_current_song()]['artist']}" )

    def get_next_song(self, num):
        new_song_index = self.current_song + num
        if new_song_index >= len(self.played_list):
            num_to_add = new_song_index - len(self.played_list) + 1
            for i in range(num_to_add):
                self.pick_new_song()

            new_song_index = len(self.played_list) - 1

        if new_song_index < 0:
            new_song_index = 0

        return new_song_index

    def pick_new_song(self):    
        picked_song = 0
        if self.shuffle:
            picked_song = random.randint(0, len(self.available_songs) - 1)
        
        self.current_song += 1

        self.used_songs.append(self.available_songs[picked_song])
        self.played_list.append(self.available_songs[picked_song])
        self.available_songs.pop(picked_song)

        if len(self.played_list) > (len(self.available_songs) + len(self.used_songs)) :
            self.played_list.pop(0)
            self.current_song -= 1

        if self.loop and len(self.used_songs) > 0.2 * (len(self.available_songs) + len(self.used_songs)):
            self.available_songs.append(self.used_songs.pop(0))

    def music_loop(self, shuffle=True, loop=True, album=None, artist=None, playlist=None):
        self.shuffle = shuffle
        self.loop = loop

        if album:
            try:
                self.available_songs = self.albums[album]["songs"]
            except:
                print(f"Album {album} not found!")
        elif artist:
            try:
                self.available_songs = self.artists[artist]["songs"]
            except:
                print(f"Artist {artist} not found!")
        elif playlist:
            pass
        else:
            self.available_songs = list(self.songs.keys())

        self.current_song = self.get_next_song(0)

        while True:
            if not self.player_lock:
                self.play() 
            else:
                self.player_lock = not self.music_player.is_running()

            if not self.player_lock:
                self.music_player.wait()

    def lyric_loop(self):
        while True:
            if "lyrics" in self.songs[self.get_current_song()].keys() and not self.is_paused() and self.lyric_index < len(self.songs[self.get_current_song()]["lyrics"]) and self.get_play_time() > self.songs[self.get_current_song()]["lyrics"][self.lyric_index][1]:
                print(self.songs[self.get_current_song()]["lyrics"][self.lyric_index][0])
                self.lyric_index += 1

            time.sleep(0.1)

class MusicSetup:
    def __init__(self):
        pass

    def initialize_all_music(self, do_lyrics):
        duration_re = re.compile(r"\d+\.\d+")

        artists = {}
        albums = {}
        songs = {}

        artist_list = next(os.walk("./music/music_library"))[1]
        
        for artist in artist_list:
            tags = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "system", "content": f"Create a list of tags for the band {artist}, seperated by ', '"}])

            similar_bands = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[
                {"role": "system", "content": f"{artist_list}"},
                {"role": "system", "content": f"Create a list of bands from the provided list that are similar to {artist}, seperated by ', '"}    
            ])

            artists[artist] = {
                "name": artist,
                "albums": [],
                "songs": [],
                "tags": tags.choices[0].message.content.split(", "),
                "similar_to": similar_bands.choices[0].message.content.split(", ")
            }

            album_list = next(os.walk(f"./music/music_library/{artist}"))[1]
            for album in album_list:
                artists[artist]["albums"].append(album)

                albums[album] = {
                    "name": album,
                    "artist": artist,
                    "songs": []
                }
                
                album_hash = str(hash(album))
                
                song_list = next(os.walk(f"./music/music_library/{artist}/{album}"))[2]
                for song in song_list:
                    song_name = song.replace(".mp3", album_hash)
                    song_link = f"./music/music_library/{artist}/{album}/{song}"

                    args = ("ffprobe","-show_entries", "format=duration", "-i", song_link)
                    popen = subprocess.Popen(args, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
                    popen.wait()
                    output = popen.stdout.read()

                    artists[artist]["songs"].append(song_name)
                    albums[album]["songs"].append(song_name)


                    songs[song_name] = {
                        "name": song.replace(".mp3", ""),
                        "album": album,
                        "artist": artist,
                        "link": song_link,
                        "duration": duration_re.search(str(output)).group(0)
                    }

                    if do_lyrics:
                        songs[song_name]["lyrics"] = self.generate_song_lyrics(song_name, song_link)

        with open("music/artists.json", 'w') as fp:
            json.dump(artists, fp)

        with open("music/albums.json", 'w') as fp:
            json.dump(albums, fp)

        with open("music/songs.json", 'w') as fp:
            json.dump(songs, fp)

    def add_lyrics_to_songs(self):
        with open("music/songs.json", 'rb') as fp:
            songs = json.load(fp)

            for (id, song_data) in songs.items():
                if not "lyrics" in song_data.keys(): 
                    print(id)
                    songs[id]["lyrics"] = self.generate_song_lyrics(song_data["name"], song_data["link"])

                    with open("music/songs.json", 'w') as f:
                        json.dump(songs, f)


    def generate_song_lyrics(self, song_name, file_link):
        audio = whisper.load_audio(file_link)

        model = whisper.load_model("large-v2", device="cpu")

        result = whisper.transcribe(model, audio, language="en", initial_prompt=f"Transcribe the song lyrics for {song_name}")

        lines = result["segments"]
        
        lyrics = []

        for line in lines:
            lyrics.append((line["text"], line["start"]))
        
        return lyrics