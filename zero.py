import socket
from flask import Flask, request, jsonify
import requests
import threading, signal
import time
import json

from music.music import MusicController
from new_server_architecture.assistant import Assistant

from config.config_variables import assistant_mode

def stable_hash(text:str):
    hash=0
    for ch in text:
        hash = ( hash*281  ^ ord(ch)*997) & 0xFFFFFFFF
    return hash

class Server:
    def __init__(self, room):
        #Creates the flask app to run the project   
        self.app = Flask(__name__)
        self.lumo_hub = None

        self.room = room
        
        self.music_controller = MusicController()
        
        self.is_online = True

        self.get_lumo_hub()

        self.assistant = Assistant(mode=assistant_mode, voice="lumo", room=room, server=self.lumo_hub)

        # self.app.route("/control_music", methods=['POST'])(self.control_music)

        threading.Thread(target=self.listen_for_devices, name="lumo_listener").start()
        threading.Thread(target=self.heartbeat, name="heartbeat_thread").start()

        signal.signal(signal.SIGINT, signal.SIG_DFL)

        self.app.run(host="0.0.0.0", port=8001)

    def get_lumo_hub(self, broadcast_ip="255.255.255.255", port=31415, timeout=2):
        buffer_size = 1024

        # Create a UDP socket for broadcasting
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(timeout)

        message = f"LumoHubDiscover,{self.room}"

        try:
            sock.sendto(message.encode(), (broadcast_ip, port))

            while True:
                try:
                    data, addr = sock.recvfrom(buffer_size)
                    response = data.decode()
                    parsed_response = response.split(",")

                    if parsed_response[0] == "LumoFound":
                        self.lumo_hub = f"{addr[0]}:{parsed_response[1]}"
                    
                except socket.timeout:
                    break  # No more responses
        finally:
            sock.close()
    
    def listen_for_devices(self):
        listen_port = 31415
        buffer_size = 1024

        # Create a UDP socket for listening
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("0.0.0.0", listen_port))

        while True:
            data, addr = sock.recvfrom(buffer_size)
            message = data.decode().split(",")

            # Check if the received message is the discovery request
            if message[0] == "LumoZeroDiscover":
                self.lumo_hub = addr[0]
                response = f"LumoFound,{self.room}"
                sock.sendto(response.encode(), addr)

    def get_ip_address(self):
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        return ip
    
    def heartbeat(self):
        while True:
            if not self.is_online and self.get_ip_address()[0:3] != "127":
                self.get_lumo_hub()

            self.is_online = self.get_ip_address()[0:3] != "127"
            time.sleep(1)

if __name__ == "__main__":
    hub = Server("bedroom")