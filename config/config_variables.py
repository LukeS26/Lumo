# What you want the AI to call you. In future this might be replaced with a classifier to detect specific voices
name = ""

#What room the assistant is in
room = ""

api_credentials = {
    "openai": {
        "key": ""
    },
    "elevenlabs": {
        "key": ""
    },
    "openweathermap": {
        "appid": ""
    },
    "twilio": {
        "sid": "",
        "auth_token": ""
    },
    "google": {
        "search_key": "",
        "map_key": ""
    }
}

latitude = 0
longitude = 0

assistant_mode = "calibrate"

enabled_features = {
    "connect_from_anywhere": True,
    "texting": True,
    "weather": True,
    "image_generation": True,
    "location_search": True,
    "wikipedia_search": True
}

# imperial or metric
measurement_units = "imperial"

contacts = {
    "name": "number"
}