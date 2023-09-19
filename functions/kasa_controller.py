import kasa
import asyncio
from thefuzz import process
import json
import time

colors = {
  "red": [0, 100, 100],
  "orange": [30, 100, 100],
  "yellow": [60, 100, 100],
  "green": [120, 100, 100],
  "blue": [240, 100, 100],
  "purple": [300, 100, 100],
  "pink": [330, 100, 100],
  "cyan": [180, 100, 100],
  "magenta": [300, 100, 100],
  "white": [0, 0, 100],
  "warm_white": [30, 10, 100],
  "cool_white": [210, 10, 100]
}

async def checkKasaBulbs(addr):
    try:
        bulb = await kasa.Discover.discover_single(addr)
        name = bulb.alias.lower().replace(" ", "_").replace("'", "")
        return (bulb, name)
    except kasa.SmartDeviceException:
        return (None, addr)

class KasaController:
    def __init__(self):
        self.devices = {}
        self.rooms = {}

        self.loop = asyncio.get_event_loop()

        self.loop.run_until_complete(self.discover())

    async def discover(self):
        with open("functions/smart_devices.json") as f:
            json_data = json.load(f)
        
        # Remove duplicate ip addresses
        json_data["lights"]["kasa"] = set(json_data["lights"]["kasa"])

        kasa.TPLinkSmartHomeProtocol.DEFAULT_TIMEOUT = 1
        
        bulb_discoveries = []

        for addr in json_data["lights"]["kasa"]:
            bulb_discoveries.append(checkKasaBulbs(addr))
        
        bulb_discoveries = await asyncio.gather(*bulb_discoveries)

        for bulb, identifier in bulb_discoveries:
            if bulb is None:
                json_data["lights"]["kasa"].remove(identifier)
            else:
                room_guess = process.extractOne(identifier, self.rooms.keys())
                if len(self.rooms) < 1 or room_guess[1] < 75: 
                    self.rooms[identifier] = [bulb]
                else:
                    self.rooms[room_guess[0]].append(bulb)

        kasa.TPLinkSmartHomeProtocol.DEFAULT_TIMEOUT = 5

        devices = await kasa.Discover.discover()

        for ip,device in devices.items():
            if device.is_bulb:
                if ip not in json_data["lights"]["kasa"]:
                    json_data["lights"]["kasa"].add(ip)
                    name = device.alias.lower().replace(" ", "_").replace("'", "")
                    room_guess = process.extractOne(name, self.rooms.keys())
                    if len(self.rooms) < 1 or room_guess[1] < 75: 
                        self.rooms[name] = [device]
                    else:
                        self.rooms[room_guess[0]].append(device)
            else:
                self.devices[device.alias] = device

        json_data["lights"]["kasa"] = list(json_data["lights"]["kasa"])

        with open("functions/smart_devices.json", 'w') as f:
            json.dump(json_data, f)

        print(self.rooms)

    async def set_room(self, name="", on="", brightness="", color=""):
        name = name.lower().replace(" ", "_")

        closest_name = process.extractOne(name, self.rooms.keys())

        if closest_name[1] < 75:
            return (404, "Room Not Found")
        
        color = color.lower().replace(" ", "_")

        for bulb in self.rooms[closest_name[0]]:
            await bulb.update()
            
            if color in colors.keys():
                if brightness:
                    await bulb.set_hsv(colors[color][0], colors[color][1], int(brightness))
                else:
                    await bulb.set_hsv(colors[color][0], colors[color][1], bulb.brightness)

            elif brightness:
                await bulb.set_brightness(int(brightness))

            if on == "on":
                await bulb.turn_on()
            elif on=="off":
                await bulb.turn_off()
            
            await bulb.update()

            return (200, "Success")
        
    async def adjust_room_brightness(self, name="", dir="", brightness=20):
        name = name.lower().replace(" ", "_")

        if not name in self.rooms.keys():
            return (404, "Room Not Found")
        
        brightness = int(brightness)

        for bulb in self.rooms[name]:
            await bulb.update()

            if dir == "down":
                brightness *= -1

            await bulb.set_brightness( bulb.brightness + brightness )
            await bulb.update()

        return (200, "Success")
    
    async def alert(self, room:str, color:str):
        old_state = []
        for bulb in self.rooms[room]:
            await bulb.update()
            old_state.append(bulb.light_state)
            await bulb.turn_on()
        
        for l in range(5):
            for i in range(len(self.rooms[room])):
                bulb = self.rooms[room][i]
                await bulb.set_hsv(colors[color][0], colors[color][1], colors[color][2], transition=150)
                await asyncio.sleep(0.35)
                await bulb.set_light_state(old_state[i], transition=150)
                await asyncio.sleep(0.5)