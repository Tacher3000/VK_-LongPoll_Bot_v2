import time
import datetime
import pytz
import random
from vk_api.utils import get_random_id
from file_manager import FileManager
from weather_service import WeatherService

SLOVAR = {
    'привет': 'Привет!',
    'как дела': 'Хорошо, а у тебя?',
    'как дела?': 'иди нахуй(без обид)',
    'воткинск': 'Столица мира'
}

WARNING_DAYS = 5
DEADLINE_DAYS = 7

class MessageHandler:
    def __init__(self, vk, longpoll, file_manager, admin_ids, trusted_ids):
        self.vk = vk
        self.longpoll = longpoll
        self.file_manager = file_manager
        self.weather_service = WeatherService()
        self.admin_ids = admin_ids
        self.trusted_ids = trusted_ids

    def handle_message(self, event):
        request = event.text.lower()
        user_id = event.user_id

        self.log_message(event, request)

        if user_id not in self.admin_ids and user_id not in self.trusted_ids:
            # self.send_message(user_id, 'У вас нет прав на выполнение этой команды.')
            return

        if request in SLOVAR:
            self.send_message(user_id, SLOVAR[request])
        elif request == '!погода':
            self.weather_service.get_weather(user_id, self.vk, self.longpoll)
        elif request == '!дневник':
            self.file_manager.send_diary(user_id, 'Мой дневник, сообщение отправлено автоматически')
        elif request == '!записать дневник':
            self.file_manager.add_diary(event.text)
        elif request == '!картинка':
            photo = self.file_manager.download_images_yadisk()
            self.file_manager.send_images(user_id, 'Вот ваша картинка', photo)
        else:
            self.send_message(user_id, 'Команда не распознана')

    def send_message(self, user_id, message):
        self.vk.messages.send(
            peer_id=user_id,
            message=message,
            random_id=get_random_id()
        )

    def log_message(self, event, message):
        with open('data/txt/history_message.txt', 'a', encoding='utf-8') as file:
            file.write(f"{event.datetime}\tпользователь {event.user_id} написал: {message}\n")
