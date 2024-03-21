import asyncio
import elevenlabs
from elevenlabs.client import ElevenLabs
from datetime import datetime, timedelta
import requests
import threading, signal
import json
from PIL import Image

import assistant.transcribe as transcribe
from config.config_variables import api_credentials, name

assistant_voice = {
    "luma": "nmVu5pKR445tWxY6JPEF",
    "lumo": "PWVNbNOu8k3hfTOGzHaX"
}

elevenlabs_client = ElevenLabs(api_key=api_credentials["elevenlabs"]["key"])

class Assistant:
    def __init__(self, mode="audio", voice="lumo", room="none"):
        self.live_transcribe = transcribe.StreamHandler()
        self.mode = mode
        self.last_valid_request = None
        self.voice = elevenlabs.Voice(
            voice_id=assistant_voice[voice],
            settings=elevenlabs.VoiceSettings(stability=0.71, similarity_boost=0.5, style=0.0, use_speaker_boost=True)
        )
        self.room = room

        self.gui = None

        threading.Thread(target=self.start).start()

        signal.signal(signal.SIGINT, signal.SIG_DFL)

    def set_server(self, server):
        self.server_ip = f"{server[0]}:{server[1]}"

    def start(self):
        if self.mode == "calibrate":
            self.live_transcribe.calibrate(25)

        if self.mode in ["audio", "calibrate"]:
            self.live_transcribe.listen(self.audio_callback, "The transcript is a request to an AI assistant named Lumo")

        elif self.mode in ["read", "text"]:
            while True:
                text = input(f"{name}: ")
                self.makeRequest(text, name)

    async def read(self, text):
        print(f"Lumo: {text}")
        # self.gui.send_response(text)

        if self.mode in ["read", "audio", "calibrate"]:
            audio = elevenlabs_client.generate(
                text=text,
                voice=self.voice,
                model="eleven_multilingual_v2"
            )
            
            elevenlabs.play(audio)

    def makeRequest(self, text, user_id):
        response = requests.post(f"http://{self.server_ip}/make_request", data={
            "message": text,
            "user": user_id,
            "room": self.room
        })

        lumo_response = response.json()["response"]

        for line in lumo_response:
            if line["role"] == "image":
                try:
                    #TODO: IMAGES CURRENTLY SLIGHTLY BROKEN, NEED TO FINISH FIXING
                    print(f"/image?image={line['content']}")
                    # img = Image.open(requests.get(f"{self.ext_req_url}/image?image={line['content']}", stream=True).raw)
                    # img.show()
                except Exception as e:
                    print(e)
            else:
                asyncio.run(self.read(line["content"]))

    def audio_callback(self, text:str, start_transcription_time):
        valid_start = "lumo" in text.lower()
        if valid_start or (start_transcription_time and self.last_valid_request and (start_transcription_time - self.last_valid_request < timedelta(seconds=15))):
            print(f"{name}: {text}")
            self.makeRequest(text, name)
            self.last_valid_request = datetime.utcnow()
        else:
            print(f"User: (Fail)")
