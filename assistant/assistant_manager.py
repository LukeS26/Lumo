import asyncio
import elevenlabs
from datetime import datetime, timedelta
import requests
import threading, signal
import json
from PIL import Image

import assistant.transcribe as transcribe
from assistant.brain import Brain
from config.config_variables import api_credentials, name 

elevenlabs.set_api_key(api_credentials["elevenlabs"]["key"])

assistant_voice = {
    "luma": "nmVu5pKR445tWxY6JPEF",
    "lumo": "PWVNbNOu8k3hfTOGzHaX"
}

class Assistant:
    def __init__(self, mode="audio", voice="lumo", room="bedroom", server=None):
        self.live_transcribe = transcribe.StreamHandler()
        self.mode = mode
        self.last_valid_request = None
        self.voice = voice
        self.room = room
        self.server = server

        self.brain = Brain()

        threading.Thread(target=self.start).start()

        signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    def start(self):
        if self.mode == "calibrate":
            self.live_transcribe.calibrate(25)

        if self.mode in ["audio", "calibrate"]:
            self.live_transcribe.listen(self.audio_callback, "The transcript is a request to an AI assistant named Lumo")

        elif self.mode in ["read", "text"]:
            while True:
                text = input("User: ")
                self.makeRequest(text, name)

    async def read(self, text):
        print(f"{self.voice.capitalize()}: {text}")

        if self.mode in ["read", "audio", "calibrate"]:
            audio = elevenlabs.generate(
                text=text,
                voice=assistant_voice[self.voice],
                model="eleven_monolingual_v1"
            )
            
            elevenlabs.play(audio)

    def makeRequest(self, text, identified_user):
        result = self.brain.makeRequest(text, self.room, server=self.server, user=identified_user)

        for line in result:
            if line["role"] == "image":
                try:
                    img = Image.open(requests.get(f"{self.ext_req_url}/image?image={line['content']}", stream=True).raw)
                    img.show()
                except Exception as e:
                    print(e)
            else:
                asyncio.run(self.read(line["content"]))

    def audio_callback(self, text:str, start_transcription_time, identified_user:str):
        valid_start = "lumo" in text.lower()
        if valid_start or (start_transcription_time and self.last_valid_request and (start_transcription_time - self.last_valid_request < timedelta(seconds=15))):
            print(f"User: {text}")
            self.makeRequest(text, identified_user)
            self.last_valid_request = datetime.utcnow()
        else:
            print(f"User: (Fail)")
