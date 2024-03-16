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
    },
    "spotify": {
        "client_id": "",
        "client_secret": ""
    }
}

latitude = 0
longitude = 0

assistant_mode = "calibrate"

enabled_features = {
    "self_host_whisper": False,
    "self_host_llm": False
}

# imperial or metric
measurement_units = "imperial"

contacts = {
    "name": "+11111111111"
}