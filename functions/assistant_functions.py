from datetime import datetime, timedelta
from playsound import playsound
import pytz
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import requests
import openai
from base64 import b64decode
from PIL import Image
import wikipedia
import json

from config.config_variables import api_credentials, contacts, measurement_units, latitude, longitude

openai.api_key = api_credentials["openai"]["key"]

# initialize Nominatim API
geolocator = Nominatim(user_agent="voice_assistant")

timezoneFinder = TimezoneFinder()
  
main_timezone = pytz.timezone("America/New_York")

months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

def get_time():
    cur_moment = datetime.now(main_timezone)

    min_str = "00"

    if cur_moment.minute < 10:
        min_str = f"0{cur_moment.minute}"
    else:
        min_str = cur_moment.minute

    cur_time = f"{1+(cur_moment.hour-1)%12}:{min_str} {'am' if cur_moment.hour%12 == cur_moment.hour else 'pm'}"
    cur_day = f"{months[cur_moment.month-1]} {cur_moment.day}, {cur_moment.year}"
    
    return f"It is currently {cur_time} on {cur_day}."

def get_time_at(location):
    try:
        better_location = geolocator.geocode(location)

        timezone = pytz.timezone(timezoneFinder.timezone_at(lng=better_location.longitude, lat=better_location.latitude))

        cur_moment = datetime.now(timezone)
        
        min_str = "00"

        if cur_moment.minute < 10:
            min_str = f"0{cur_moment.minute}"
        else:
            min_str = cur_moment.minute

        cur_time = f"{1+(cur_moment.hour-1)%12}:{min_str} {'am' if cur_moment.hour%12 == cur_moment.hour else 'pm'}"
        cur_day = f"{months[cur_moment.month-1]} {cur_moment.day}, {cur_moment.year}"
        
        return f"In {location} it is currently {cur_time} on {cur_day}."
    except:
        return f"Could not find the time in {location}"

def send_text(twilio_client, contact_name, message):
    try:
        contact_name = contact_name.lower()
        
        if not contact_name in contacts:
            return f"It appears there is no contact in your phone by the name of {contact_name}, would you like to send the message to a different person?"

        message = twilio_client.messages.create(
            from_='+18334970620',
            body="\n".join(message.splitlines()),
            to=f'+1{contacts[contact_name]}'
        )

        print(message.sid)

        return f"Just sent the text message to {contact_name}, is there anything else you would like me to do?"
    except Exception as e:
        return f"Error, could not send message to {contact_name}: {e}"

def get_weather(request):
    try:
        response = requests.get(f"https://api.openweathermap.org/data/3.0/onecall?lat={latitude}&lon={longitude}&appid={api_credentials['openweathermap']['appid']}&units={measurement_units}&exclude=minutely,alerts")
        
        forecast_info = { }

        day_of_week = datetime.now(main_timezone).weekday()
        day_as_text = "Today"
        
        for day in range(0, 8):
            if(day == 1): 
                day_as_text = "Tomorrow"

            forecast_info[day_as_text] = {
                "temperature": response.json()['daily'][day]['temp']['day'],
                "high": response.json()['daily'][day]['temp']['max'],
                "low": response.json()['daily'][day]['temp']['min'],
                "description": response.json()['daily'][day]["summary"]
            }

            day_of_week += 1
            day_of_week %= 7
            day_as_text = days_of_week[day_of_week]
        
        current_hour = datetime.now(main_timezone).hour

        for i in range (0, 12):
            forecast_info["Today"][f"{current_hour + i}00"] = {
                "description": response.json()['hourly'][i]["weather"][0]["description"],
                "temperature": response.json()['hourly'][i]["temp"],
                "chance_of_precipitation": response.json()['hourly'][i]["pop"]
            }
        
        chat_completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[
            {"role": "system", "content": json.dumps(forecast_info)},
            {"role": "system", "content": f"summarize the above weather information to best answer the following request about the weather: {request}"}
        ])
        
        return chat_completion.choices[0].message.content
    except Exception as err:
        return f"Error: {err}, could not find weather"

def get_weather_at(location, request):
    try:
        better_location = geolocator.geocode(location)

        response = requests.get(f"https://api.openweathermap.org/data/3.0/onecall?lat={better_location.latitude}&lon={better_location.longitude}&appid={api_credentials['openweathermap']['appid']}&units={measurement_units}&exclude=minutely,alerts")
        
        forecast_info = { }

        day_of_week = datetime.now(main_timezone).weekday()
        day_as_text = "Today"
        
        for day in range(0, 8):
            if(day == 1): 
                day_as_text = "Tomorrow"

            forecast_info[day_as_text] = {
                "temperature": response.json()['daily'][day]['temp']['day'],
                "high": response.json()['daily'][day]['temp']['max'],
                "low": response.json()['daily'][day]['temp']['min'],
                "description": response.json()['daily'][day]["summary"]
            }

            day_of_week += 1
            day_of_week %= 7
            day_as_text = days_of_week[day_of_week]
        
        current_hour = datetime.now(main_timezone).hour

        for i in range (0, 12):
            forecast_info["Today"][f"{current_hour + i}00"] = {
                "description": response.json()['hourly'][i]["weather"][0]["description"],
                "temperature": response.json()['hourly'][i]["temp"],
                "chance_of_precipitation": response.json()['hourly'][i]["pop"]
            }
        
        
        chat_completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[
            {"role": "system", "content": json.dumps(forecast_info)},
            {"role": "system", "content": f"summarize the above weather information to best answer the following request about the weather: {request} at {location}"}
        ])
        
        return chat_completion.choices[0].message.content
    except:
        return f"Error, could not find weather at {location}"

def generate_image(prompt):
    try:
        image = openai.Image.create(
            prompt=prompt,
            n=1,
            size="1024x1024",
            response_format="b64_json"
        )

        image_data = b64decode(image["data"][0]["b64_json"])
        image_file = f"static/images/{prompt[:32].replace(' ', '_')}{image['created']}.png"
        with open(image_file, mode="wb") as png:
            png.write(image_data)

        return [f"Generated image with prompt {prompt}", image_file]
    except:
        return [f"Could not generate image with prompt {prompt}"]

def generate_image_message(prompt):
    try:
        image = openai.Image.create(
            prompt=prompt,
            n=1,
            size="1024x1024",
            response_format="b64_json"
        )

        image_data = b64decode(image["data"][0]["b64_json"])
        image_file = f"static/images/{prompt[:32].replace(' ', '_')}{image['created']}.png"
        with open(image_file, mode="wb") as png:
            png.write(image_data)

        return image_file
    except:
        return

def search_web(query):
    try:
        response = requests.get(f"https://www.googleapis.com/customsearch/v1?key={api_credentials['google']['search_key']}&cx=d0abc540d199c44a9&q={query}")

        wiki_query = wikipedia.search(response.json()["items"][0]["title"][:-12], results=1)[0]

        summary = wikipedia.summary(wiki_query)

        chat_completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[
            {"role": "system", "content": summary},
            {"role": "system", "content": f"summarize the above information to best answer the query: {query}"}
        ])
        
        return chat_completion.choices[0].message.content
    except:
        return f"Error, query {query} could not be completed"


def find_nearby_locations(location_type, location=None):
    try:
        used_latitude = latitude
        used_longitude = longitude
        if not location is None:
            print(location)
            better_location = geolocator.geocode(location)

            used_latitude = better_location.latitude
            used_longitude = better_location.longitude

        response = requests.get(f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?key={api_credentials['google']['map_key']}&location={latitude},{longitude}&keyword={location_type}&rankby=distance").json()

        locations = ""

        weekday = datetime.now(main_timezone).weekday()

        for place in response["results"][:12]:
            open_hours = requests.get(f"https://maps.googleapis.com/maps/api/place/details/json?key={api_credentials['google']['map_key']}&reference={place['place_id']}").json()
            open_hours = (open_hours)["result"]

            if not "opening_hours" in open_hours.keys():
                continue

            locations += f"{place['name']}: "  

            if not open_hours["opening_hours"]["open_now"]:
                if not "Closed" in open_hours['opening_hours']['weekday_text'][(weekday+1)%7]: 
                    locations += f"Open tomorrow from {open_hours['opening_hours']['weekday_text'][(weekday+1)%7].split(': ')[1]}"
                else:
                    for i in range(len(open_hours['opening_hours']['weekday_text'])):
                        if not "Closed" in open_hours['opening_hours']['weekday_text'][(weekday+1+i)%7]: 
                            locations += f"Open {days_of_week[(weekday+1+i)%7]} from {open_hours['opening_hours']['weekday_text'][(weekday+1+i)%7].split(': ')[1]}"
                            break
            else:
                if "–" in open_hours['opening_hours']['weekday_text'][weekday]: 
                    locations += f"Open until{open_hours['opening_hours']['weekday_text'][weekday].split('–')[1]}"
                elif ": " in open_hours['opening_hours']['weekday_text'][weekday]:
                    locations += f"{open_hours['opening_hours']['weekday_text'][weekday].split(': ')[1]}"

            locations += "\n"

        return locations
    except:
        return "Error, could not find locations"

def wake_up():
    return f"Good morning. {get_weather('Get an overview of the upcoming weather over the next 12 hours')}"