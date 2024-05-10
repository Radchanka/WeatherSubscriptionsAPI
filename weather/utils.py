import os
import requests
from dotenv import load_dotenv

load_dotenv()


def get_weather(city_data):
    OWM_TOKEN = os.environ.get('OWM_TOKEN')
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city_data['name']},{city_data['state']}," \
          f"{city_data['country_code']}&appid={OWM_TOKEN}&units=metric"
    weather_resp = requests.get(url).json()

    if weather_resp['cod'] != 200:
        res = {'message': weather_resp['message']}
        code = weather_resp['cod']
    else:
        res = {
            'weather_description': weather_resp['weather'][0]['description'],
            'temperature': weather_resp['main']['temp'],
            'feels_like': weather_resp['main']['feels_like'],
            'humidity': weather_resp['main']['humidity'],
            'pressure': weather_resp['main']['pressure'],
            'visibility': weather_resp['visibility'],
            'wind_speed': weather_resp['wind']['speed'],
            'clouds': weather_resp.get('clouds', {}).get('all', 0),
            'rain': weather_resp.get('rain', {}).get('1h', 0),
            'snow': weather_resp.get('snow', {}).get('1h', 0),
        }
        code = 200

    return res, code
