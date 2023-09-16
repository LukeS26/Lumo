import kasa
import asyncio

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

class KasaController:
    def __init__(self):
        self.devices = {
        }

        self.rooms = {
            "room_name": [ kasa.SmartBulb("IP") ]
        }

    async def set_room(self, name="", on="", brightness="", color=""):
        name = name.lower().replace(" ", "_")

        if not name in self.rooms.keys():
            return (404, "Room Not Found")
        
        color = color.lower().replace(" ", "_")

        for bulb in self.rooms[name]:
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
    
    async def alert(self, room:str):
        old_state = []
        for bulb in self.rooms[room]:
            await bulb.update()
            old_state.append(bulb.light_state)
            await bulb.turn_on()
        
        for l in range(5):
            for i in range(len(self.rooms[room])):
                bulb = self.rooms[room][i]
                await bulb.set_hsv(275, 100, 100, transition=150)
                await asyncio.sleep(0.15)
                await bulb.set_light_state(old_state[i], transition=250)
                await asyncio.sleep(0.25)