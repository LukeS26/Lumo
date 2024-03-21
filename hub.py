import socket
from flask import Flask, request, jsonify
import requests
import threading, signal
import time
import json
from pyngrok import ngrok


from new_server_architecture.brain import Brain
from new_server_architecture.mpd_handler import MPDHandler
from new_server_architecture.twilio_controller import TwilioController

def stable_hash(text:str):
    hash=0
    for ch in text:
        hash = ( hash*281  ^ ord(ch)*997) & 0xFFFFFFFF
    return hash

class Server:
    def __init__(self, port=8001):
        #Creates the flask app to run the project   
        self.app = Flask(__name__)

        self.port = port

        # Format is {"room_name": "ip"}
        self.device_list = {}
        
        self.brain = Brain()

        self.mpd_handler = MPDHandler()
        self.twilio_handler = TwilioController(self.brain)

        self.brain.twilio_client = self.twilio_handler

        self.is_online = True

        self.get_all_devices()

        self.app.route("/make_request", methods=['POST'])(self.process_request)
        self.app.route("/control_music_playback", methods=['POST'])(self.control_mpd_playback)
        self.app.route("/sms", methods=['POST'])(self.handle_sms)

        threading.Thread(target=self.listen_for_devices, name="lumo_listener").start()
        threading.Thread(target=self.heartbeat, name="heartbeat_thread").start()

        signal.signal(signal.SIGINT, signal.SIG_DFL)

        url = ngrok.connect(self.port, domain="remarkably-immortal-calf.ngrok-free.app").public_url
        print(' `* Tunnel URL:', url)

        self.twilio_handler.update_url(url)

        self.app.run(host="0.0.0.0", port=self.port)

    def process_request(self):
        return {"response": self.brain.make_request(request.form.get("message"), request.form.get("room"), request.form.get("user"))}

    #Endpoint is only needed for eventual webpage/phone apps
    def control_mpd_playback(self):
        pass

    def handle_sms(self):
        resp = self.twilio_handler.respond_to_text(request)
        if resp:
            return resp
        return ""

    def get_all_devices(self, broadcast_ip="255.255.255.255", port=31415, timeout=2):
        buffer_size = 1024

        # Create a UDP socket for broadcasting
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(timeout)

        message = f"LumoZeroDiscover,{self.port}"

        try:
            sock.sendto(message.encode(), (broadcast_ip, port))

            while True:
                try:
                    data, addr = sock.recvfrom(buffer_size)
                    response = data.decode()
                    parsed_response = response.split(",")

                    if parsed_response[0] == "LumoFound":
                        room_name = parsed_response[1]
                        self.device_list[room_name] = addr[0]
                    
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
            parsed_response = data.decode().split(",")

            # Check if the received message is the discovery request
            if parsed_response[0] == "LumoHubDiscover":
                room_name = parsed_response[1]
                self.device_list[room_name] = addr[0]
                sock.sendto(f"LumoFound,{self.port}".encode(), addr)

    def get_ip_address(self):
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        return ip
    
    def heartbeat(self):
        while True:
            if not self.is_online and self.get_ip_address()[0:3] != "127":
                self.get_all_devices()

            self.is_online = self.get_ip_address()[0:3] != "127"
            time.sleep(1)
            
if __name__ == "__main__":
    hub = Server()
