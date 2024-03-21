import os
import shutil
import subprocess
import time
import mpd
import threading

class MPDServer:
    def __init__(self, port):
        self.port = port
        self.http_port = port + 1  # Assuming HTTP port is MPD port + 1
        self.config_file = f"/tmp/mpd_{port}.conf"
        self.pid_file = f"/tmp/mpd_{port}.pid"
        self.music_directory = f"{os.path.abspath(os.getcwd())}/music/music_library"
        self.mpd_client = mpd.MPDClient()

        self.running = True

        self.song_pick_thread = threading.Thread(target=self.song_picker, name=f"song_picker_{self.port}")
        self.song_pick_thread.start()

    def song_picker(self):
        while self.running:
            response = client.idle("playlist")
            if "playlist" in response:
                playlist = client.playlistinfo()
                if len(playlist) == 0:
                    self.pick_new_song()

    def create_config(self):
        with open(self.config_file, "w") as f:
            f.write(f"music_directory \"{self.music_directory}\"\n")
            f.write(f"pid_file \"{self.pid_file}\"\n")
            f.write(f"port \"{self.port}\"\n")
            f.write("audio_output {\n")
            f.write(f"    type            \"httpd\"\n")
            f.write(f"    name            \"HTTP Stream on port {self.http_port}\"\n")
            f.write(f"    encoder         \"lame\"\n")
            f.write(f"    port            \"{self.http_port}\"\n")
            f.write(f"    quality         \"5.0\"\n")  # Adjust quality as needed
            f.write("}\n")
            f.write("bind_to_address \"::1\"\n")  # Bind to localhost

    def start_server(self):
        subprocess.Popen(["mpd", "--no-daemon", self.config_file])

    def connect(self):
        self.mpd_client.connect("localhost", self.port)

    def close(self):
        self.mpd_client.close()
        self.mpd_client.disconnect()

    def cleanup(self):
        os.remove(self.config_file)
        if os.path.exists(self.pid_file):
            os.remove(self.pid_file)

    def toggle_pause(self, should_pause:bool):
        self.mpd_client.pause(int(should_pause))

    def start(self):
        self.mpd_client.play()

    def queue_song(self, song_id):
        self.mpd_client.add()

    def queue_album(self, album_id):
        self.mpd_client.add()

def make_new_mpd_server():
    port = find_available_port()
    server = MPDServer(port)
    server.create_config()
    server.start_server()
    time.sleep(1)  # Allow time for server to start
    server.connect()
    return server

def find_available_port(start_port=6600):
    port = start_port
    while is_port_in_use(port) or is_port_in_use(port + 1):  # Check both MPD and HTTP ports
        port += 2  # Increment by 2 to ensure different ports for MPD and HTTP
    return port

def is_port_in_use(port):
    with subprocess.Popen(["lsof", "-i", f":{port}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
        result = proc.stdout.read().decode()
    return bool(result)

class MPDHandler:
    def __init__(self):
        self.servers = {}
        self.room_links = {}

    def create_server(self, room_name:str):
        server = make_new_mpd_server()
        self.servers[server.port] = (server, [room_name])
        
        if room_name in self.room_links.keys():
            old_server = self.room_links[room_name]
            self.servers[old_server][1].remove(room_name)
            if len(self.servers[old_server][1]) == 0:
                self.servers[old_server][0].close()
                self.servers[old_server][0].cleanup()
                del self.servers[old_server]
        
        self.room_links[room_name] = server.port
        print(f"MPD server started on port {server.port}")

    def link_rooms(self, room_a, room_b):
        room_a_server = self.room_links[room_a]
        room_b_server = self.room_links[room_b]

        self.servers[room_a_server][1].remove(room_a)
        self.servers[room_b_server][1].append(room_a)

        self.room_links[room_a] = room_b_server

        if len(self.servers[room_a_server][1]) == 0:
            self.servers[room_a_server][0].close()
            self.servers[room_a_server][0].cleanup()
            del self.servers[room_a_server]

    def control_server(self, port):
        server = self.servers[port][1]
        
        server.mpd_client

    def control_server_by_room(self, room):
        self.control_server(self.room_links[room])

    def cleanup_server(self):
        for port, server in self.servers.items():
            server[0].close()
            server[0].cleanup()