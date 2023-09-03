from flask import Flask, request, send_file, jsonify
from pyngrok import ngrok
import asyncio

from functions.twilio_response import TwilioHandler
from assistant.brain import Brain

class CentralServer:
    def __init__(self):
        self.app = Flask(__name__)
        self.brain = Brain()
        
        self.assistants = {}

        self.app.route("/check_online", methods=["GET"])(lambda: "online")
        self.app.route("/connect_assistant", methods=['POST'])(self.connect_assistant)
        self.app.route("/query_transcription", methods=['POST'])(self.handle_request)
        self.app.route("/clear_chat_history", methods=['POST'])(self.delete_chat)
        self.app.route("/toggle_light", methods=["POST"])(self.toggle_light)

    def connect_assistant(self):
        self.assistants[request.values["room_name"]] = f"{request.values['ip']}:8000"
        return "success"

    def handle_request(self):
        return jsonify(self.brain.makeRequest(request.values["text"], request.values["room"]))

    def delete_chat(self):
        return self.brain.clear_chat()

    def toggle_light(self):
        if not request.json["room"] or not request.json["state"]:
            print("ERROR")
            return "ERROR"
        else:
            asyncio.run(self.brain.kasa_controller.set_room(request.json["room"], on=request.json["state"]))

        return "Success"

    def start(self, room_ip, room_name):
        self.assistants[room_name] = f"{room_ip}:8001"
        self.app.run(host="0.0.0.0", port=8000)       