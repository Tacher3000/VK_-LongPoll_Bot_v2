import requests
import os

from vk_api.longpoll import VkEventType
from vk_api.utils import get_random_id


class WeatherService:
    def __init__(self):
        self.api_key = os.getenv('WATER_TOKEN')
        self.base_url = "http://api.openweathermap.org/data/2.5/forecast?"

    def get_weather(self, user_id, vk, longpoll):
        vk.messages.send(peer_id=user_id, message='Введите название города:', random_id=get_random_id())
        city_name = self.listen_for_response(user_id, longpoll)

        vk.messages.send(peer_id=user_id, message='Выберите прогноз погоды: 1 - сейчас, 2 - на сегодня, 3 - на 3 дня вперед:', random_id=get_random_id())
        forecast_choice = self.listen_for_response(user_id, longpoll)

        complete_url = self.base_url + "appid=" + self.api_key + "&q=" + city_name + "&units=metric"
        response = requests.get(complete_url)
        data = response.json()

        if data["cod"] != "404":
            if forecast_choice == '1':
                current_temp = data['list'][0]['main']['temp']
                vk.messages.send(peer_id=user_id, message=f"Текущая температура в городе {city_name} : {current_temp}°C", random_id=get_random_id())
            elif forecast_choice == '2':
                today_temp = data['list'][0]['main']['temp']
                vk.messages.send(peer_id=user_id, message=f"Температура на сегодня в городе {city_name} : {today_temp}°C", random_id=get_random_id())
            elif forecast_choice == '3':
                day1_temp = data['list'][0]['main']['temp']
                day2_temp = data['list'][1]['main']['temp']
                day3_temp = data['list'][2]['main']['temp']
                vk.messages.send(peer_id=user_id, message=f"Температура на следующие 3 дня в городе {city_name} : \nДень 1: {day1_temp}°C\nДень 2: {day2_temp}°C\nДень 3: {day3_temp}°C", random_id=get_random_id())
            else:
                vk.messages.send(peer_id=user_id, message="Вы выбрали неверный параметр прогноза погоды", random_id=get_random_id())
        else:
            vk.messages.send(peer_id=user_id, message=f"Город {city_name} не найден", random_id=get_random_id())

    def listen_for_response(self, user_id, longpoll):
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.user_id == user_id:
                return event.text
