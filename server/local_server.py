from flask import Flask, request
import socket
import requests
import threading
import signal

from assistant.assistant_manager import Assistant
from central_server import CentralServer

class AssistantServer:
    def __init__(self):
        self.app = Flask(__name__)
        self.central_server_url = ""
        self.self_ip_address = self.get_ip_address()
        self.assistant = Assistant(mode="audio", room="luke_bedroom", ext_req_url=self.central_server_url)

        self.app.route("/update_address", methods=['POST'])(self.update_address)
        self.app.route("/music_control", methods=['POST'])(self.control_music)

    def get_ip_address(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("255.255.255.255", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip

    def update_address(self):
        self.central_server_url = request.values["address"]
        self.assistant.ext_req_url = self.central_server_url
        return "OK"

    def control_music(self):
        self.assistant.music_controller.run_music_command(request.values["command"])

    def check_central(self):
        try:
            requests.get(f"{self.central_server_url}/check_online", timeout=0.5).raise_for_status()
        except (requests.Timeout, requests.RequestException):
            return False
        else:
            return True

    def connect_to_central(self):
        requests.post(self.central_server_url + "/connect_assistant", data={
            "ip": self.self_ip_address,
            "room_name": self.assistant.room
        })

    def start(self):
        central_server = CentralServer()
        
        threading.Thread(target=self.app.run, kwargs={"host": self.self_ip_address, "port": 8001}).start()

        if not self.check_central():
            threading.Thread(target=central_server.start, kwargs={"ip": self.self_ip_address, "room_name": self.assistant.room}).start()
        else:
            self.connect_to_central()

        signal.signal(signal.SIGINT, signal.SIG_DFL)
        print(self.self_ip_address)