import os
from vk_api import VkApi
from vk_api.longpoll import VkLongPoll, VkEventType
import yadisk
from vk_api.utils import get_random_id
from file_manager import FileManager
from message_handler import MessageHandler
from my_vk_longpoll import MyVkLongPoll
from trusted_people import TrustedPeople

class VKBot:
    def __init__(self, token, yadisk_token, admin_ids, trusted_ids):
        self.token = token
        self.vk_session = VkApi(token=self.token)
        self.vk = self.vk_session.get_api()
        self.longpoll = MyVkLongPoll(self.vk_session)
        self.yadisk = yadisk.YaDisk(token=yadisk_token)
        self.file_manager = FileManager(self.yadisk, self.vk)
        self.trusted_people = TrustedPeople(trusted_ids)
        self.message_handler = MessageHandler(self.vk, self.longpoll, self.file_manager, admin_ids, trusted_ids)

    def send_message(self, id, message):
        self.vk.messages.send(
            peer_id=id,
            message=message,
            random_id=get_random_id(),
        )

    def listen(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                self.message_handler.handle_message(event)

if __name__ == "__main__":
    admin_ids = list(map(int, os.getenv('ADMIN_IDS').split(',')))
    trusted_ids = list(map(int, os.getenv('TRUSTED_IDS').split(',')))
    bot = VKBot(os.getenv('VK_TOKEN'), os.getenv('YADISK_TOKEN'), admin_ids, trusted_ids)
    bot.listen()
