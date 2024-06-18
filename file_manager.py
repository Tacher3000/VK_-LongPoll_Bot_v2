import os
import datetime

import requests
import yadisk
import random
from vk_api.utils import get_random_id

class FileManager:
    def __init__(self, yadisk, vk):
        self.yadisk = yadisk
        self.vk = vk

    def send_txt_file(self, user_id, message, file_path):
        upload_url = self.vk.docs.getMessagesUploadServer(type='doc', peer_id=user_id)['upload_url']
        file = {'file': open(f'data/txt/{file_path}', 'rb')}
        response = requests.post(upload_url, files=file)
        result = response.json()
        doc = self.vk.docs.save(file=result['file'], title=file_path)['doc']
        self.vk.messages.send(
            peer_id=user_id,
            message=message,
            attachment=f"doc{doc['owner_id']}_{doc['id']}",
            random_id=get_random_id()
        )

    def send_images(self, user_id, message, images_path):
        upload_url = self.vk.photos.getMessagesUploadServer(peer_id=user_id)['upload_url']
        response = requests.post(upload_url, files={'photo': open(f'data/images/{images_path}', 'rb')}).json()
        photo_data = self.vk.photos.saveMessagesPhoto(photo=response['photo'], server=response['server'], hash=response['hash'])[0]
        attachment = f"photo{photo_data['owner_id']}_{photo_data['id']}_{photo_data['access_key']}"
        self.vk.messages.send(peer_id=user_id, message=message, attachment=attachment, random_id=get_random_id())

    def download_images_yadisk(self):
        current_date = datetime.date.today()
        day_of_week = current_date.weekday()

        path_to_day = {
            0: '/mems',
            1: '/Screenshots',
            2: '/minecraft screenshots',
            3: '/download',
            4: '/mems',
            5: '/Screenshots',
            6: '/minecraft screenshots',
        }

        path = path_to_day.get(day_of_week, '/mems')

        photo_names = [item.name for item in self.yadisk.listdir(path) if item.type == 'file']
        random_photo = random.choice(photo_names)
        self.yadisk.download(f'{path}/{random_photo}', f'data/images/{random_photo}')
        return random_photo

    def send_diary(self, user_id, message):
        self.yadisk.download('/diary.txt', 'data/txt/diary.txt')
        self.send_txt_file(user_id, message, 'diary.txt')

    def add_diary(self, message):
        self.yadisk.download('/diary.txt', 'data/txt/diary.txt')
        with open('data/txt/diary.txt', 'a', encoding='utf-8') as file:
            file.write(f'{message}\n\n')
        self.yadisk.upload('data/txt/diary.txt', '/diary.txt', overwrite=True)
