import json
import asyncio

from functions.kasa_controller import KasaController

class SmartDeviceHub:
    def __init__(self):
        self.kasa_controller = KasaController()

        with open("functions/smart_devices.json") as f:
            self.devices = json.load(f)
        
    def set_plug(self, name="", on=""):
        if name in self.devices["devices"]["kasa"]:
            self.kasa_controller.set_plug(name=name, on=on)
            return f"Turned {name} {on}."
            
        else:
            return f"No device with name {name} found."

    def set_room(self, name="", on="", brightness="", color=""):
        self.kasa_controller.set_room(name=name, on=on, brightness=brightness, color=color)

    def alert(self, room="", color=""):
        self.kasa_controller.alert(room, color)