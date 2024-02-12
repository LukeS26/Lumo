import socket
from flask import Flask, request, jsonify
import requests
import threading, signal
import time
import json

from assistant.assistant_manager import Assistant
from music.music import MusicController

class Server:
    def __init__(self, mode="audio", voice="lumo", room="bedroom"):
        #Creates the flask app to run the project   
        self.app = Flask(__name__)
        
        #Creates an assisant object, containing the local memory/brain
        self.assistant = Assistant(mode=mode, voice=voice, room=room, server=self)

        # self.music_controller = MusicController()
        
        self.is_online = True

        self.start_server()

        self.app.route("/sync_data", methods=['POST'])(self.sync_data)
        self.app.route("/request_all_data", methods=['GET'])(self.send_data)

        threading.Thread(target=self.listen_for_devices, name="lumo_listener").start()
        threading.Thread(target=self.heartbeat, name="heartbeat_thread").start()

        signal.signal(signal.SIGINT, signal.SIG_DFL)

        self.app.run(host="0.0.0.0", port=8001)

    def start_server(self):
        print("Starting Up Server")

        most_updated = self.get_all_devices()

        if most_updated:
            resp = requests.get(f"http://{most_updated}:8001/request_all_data")
            self.latest_update = time.time_ns()

            self.assistant.brain.saved_chats = resp.json()

    def update_all_servers(self, data):
        self.latest_update = time.time_ns()
        for ip in self.ip_list.keys():
            requests.post(f"http://{ip}:8001/sync_data", json=json.dumps(data))
    
    def send_data(self):
        return jsonify(self.assistant.brain.saved_chats)
    
    def sync_data(self):
        self.latest_update = time.time_ns()
        self.assistant.brain.update_data(request.json)
        return "Success"

    def get_all_devices(self, broadcast_ip="255.255.255.255", port=31415, timeout=2):
        buffer_size = 1024

        # Create a UDP socket for broadcasting
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(timeout)

        message = f"LumoDiscover,{self.assistant.room},{self.latest_update}"

        most_updated = [0, ""]

        try:
            sock.sendto(message.encode(), (broadcast_ip, port))

            while True:
                try:
                    data, addr = sock.recvfrom(buffer_size)
                    response = data.decode()
                    parsed_response = response.split(",")
                    self.ip_list[addr[0]] = parsed_response[0]
                    
                    if int(parsed_response[1]) > most_updated[0]:
                        most_updated[0] = int(parsed_response[1])
                        most_updated[1] = addr[0]
                    
                except socket.timeout:
                    break  # No more responses
        finally:
            sock.close()
            return most_updated[1]
    
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
            if message[0] == "LumoDiscover":
                self.ip_list[addr[0]] = message[1]
                response = f"{self.assistant.room},{self.latest_update}"
                sock.sendto(response.encode(), addr)

    def get_ip_address(self):
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        return ip
    
    def heartbeat(self):
        while True:
            if not self.is_online and self.get_ip_address()[0:3] != "127":
                self.start_server()

            self.is_online = self.get_ip_address()[0:3] != "127"
            time.sleep(1)