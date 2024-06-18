from vk_api.longpoll import VkLongPoll
import requests

class MyVkLongPoll(VkLongPoll):
    def listen(self):
        while True:
            try:
                for event in self.check():
                    yield event
            except requests.exceptions.ReadTimeout:
                continue
