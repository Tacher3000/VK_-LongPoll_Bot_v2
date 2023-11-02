import requests
import datetime
import pytz
import time
import os
from vk_api import VkApi
from vk_api.longpoll import VkLongPoll, VkEventType
import function as f


import os
from dotenv import load_dotenv
load_dotenv()



# через сколько дней попросят отметиться
warning = 5

# через сколько дней без отметок отправится дневник
deadline = 7


slovar = {'привет': 'Привет!',
          'как дела': 'Хорошо, а у тебя?',
          'как дела?': 'иди нахуй(без обид)',
          'воткинск': 'Столица мира'}

# чтобы не выключался каждую ночь + когда срабатывает исключение добавляется +1 и происходит проверка на колличество дней


class MyVkLongPoll(VkLongPoll):
    def listen(self):
        while True:
            try:
                for event in self.check():
                    yield event
            except Exception as e:
                print('error', e)
                time.sleep(10)


                current_timestamp = int(time.time())
                timestamp = f.marks(240453492)
                t = timestamp['time']

                # Преобразование Unix Timestamp в объект datetime
                dt_object = datetime.datetime.fromtimestamp(t, tz=pytz.UTC)

                # Получение объекта для Московского времени
                msk_tz = pytz.timezone('Europe/Moscow')
                msk_time = dt_object.astimezone(msk_tz)

                # Преобразование объекта datetime в строку в читаемом формате
                readable_msk_time = msk_time.strftime('%Y-%m-%d %H:%M:%S %Z')

                f.send_message(240453492, f'был в сети {readable_msk_time}')

                # проверка на колличество дней
                if (current_timestamp - t > warning * 24 * 60 * 60) and (current_timestamp - t < deadline * 24 * 60 * 60):
                    f.send_message(
                        240453492, f'в последний раз ты был онлайн {warning} или больше дней назад. Пожалуйста, зайди в сеть')
                    f.send_message(
                        240453492, f'через столько дней:{deadline - ((current_timestamp - t) / (24 * 60 * 60)) } дневник будет отправлен')

                if (current_timestamp - t > deadline * 24 * 60 * 60):
                    f.send_message(
                        240453492, f'ты не заходил больше {deadline} дней')
                    f.diary()
                    f.send_message(
                        240453492, 'дневник отправлен')


def main():
    print('запустилось')
    # token = f.open_txt('access_token.txt')
    token = os.environ['TOKEN']
    vk_session = VkApi(token=token)
    vk = vk_session.get_api()
    longpoll = MyVkLongPoll(vk_session)

    timestamp = f.marks(240453492)
    t = timestamp['time']

    # Преобразование Unix Timestamp в объект datetime
    dt_object = datetime.datetime.fromtimestamp(t, tz=pytz.UTC)

    # Получение объекта для Московского времени
    msk_tz = pytz.timezone('Europe/Moscow')
    msk_time = dt_object.astimezone(msk_tz)

    # Преобразование объекта datetime в строку в читаемом формате
    readable_msk_time = msk_time.strftime('%Y-%m-%d %H:%M:%S %Z')

    f.send_message(240453492, f'был в сети {readable_msk_time}')


    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.from_user:
            k = 0
            # message
            message = event.text

            # добавление в историю (отключено из-за бесполезности и ошибок)
            # f.history_message(event, message)

            # преобразование слова в нижний регистр
            message = message.lower()

            # id
            id = event.user_id

            # проверяет есть ли человек который пишет в списке администрации
            for i in range(f.count_lines('administrators.txt')):
                if id == int(f.open_txt_line(i, 'administrators.txt')):
                    if message == '!команды':
                        f.send_message(id, f.open_txt(
                            'administrators_comands.txt'))
                        k += 1
                    elif message == '!погода':
                        f.water(id, longpoll)
                        k += 1
                    elif slovar.get(message) != None:
                        f.send_message(id, slovar.get(message))
                        k += 1
                    elif message == '!отправь':
                        f.send_message(
                            id, 'Ты точно хочешь это сделать? [Y - да, N - нет]')
                        # немного переделать!!!!!!
                        for e in longpoll.listen():
                            if e.type == VkEventType.MESSAGE_NEW and e.to_me:
                                if e.text == 'Y':
                                    f.diary()
                                    break
                                else:
                                    f.send_message(id, 'Отправка отменена')
                                    break
                        k += 1
                    elif message == '!рандом':
                        random_image = f.download_images_yadisk()
                        f.send_images(id, '', random_image)
                        try:
                            os.remove('data/images/' + random_image)
                        except FileNotFoundError:
                            print(
                                'изображение для удаления не найдено(что странно).')
                        k += 1
                    elif message == '!посмотреть':
                        f.me_diary(id, '')
                        k += 1
                    elif message == '!дополнить' or message == '!добавить':
                        f.send_message(id, 'введите что хотите добавить')
                        for e in longpoll.listen():
                            if e.type == VkEventType.MESSAGE_NEW and e.to_me:
                                f.add_diary(e.text)
                                break
                        f.send_message(id, 'сообщение добавлено')
                        k += 1
                    elif message == '!инфо':
                        f.send_message(id, f.open_txt('info.txt'))
                        k += 1

            if k == 1:
                continue

            # проверка на людей из списка проверенных людей
            for i in range(f.count_lines('trusted_people.txt')):
                if id == int(f.open_txt_line(i, 'trusted_people.txt')):
                    # if (message == '!отправь'):
                    #     f.diary()
                    #     k += 1
                    if slovar.get(message) != None:
                        f.send_message(id, slovar.get(message))
                        k += 1
                    elif message == '!команды':
                        f.send_message(id, f.open_txt(
                            'trusted_people_comands.txt'))
                        k += 1
                    elif message == '!погода':
                        f.water(id, longpoll)
                        k += 1
                    elif message == '!рандом':
                        random_image = f.download_images_yadisk()
                        f.send_images(id, '', random_image)
                        try:
                            os.remove('data/images/' + random_image)
                        except FileNotFoundError:
                            print(
                                'изображение для удаления не найдено(что странно).')
                        k += 1
                    elif message == '!инфо':
                        f.send_message(id, f.open_txt('info.txt'))
                        k += 1
                    else:
                        response = vk.users.get(user_ids=id, fields='first_name,last_name')

                        user_info = response[0]
                        first_name = user_info['first_name']

                        f.send_message(
                            id, f'{first_name}, к сожалению, я всего лишь бот')
                        k += 1
                    

            # if k == 1:
            #     continue

            # if slovar.get(message) != None:

            #     f.send_message(id, slovar.get(message))
            #     k += 1
            # elif message == '!команды':
            #     f.send_message(id, f.open_txt(
            #         'comands.txt'))
            #     k += 1
            # elif message == '!погода':
            #     f.water(id, longpoll)
            #     k += 1
            # elif message == '!рандом':
            #     random_image = f.download_images_yadisk()
            #     f.send_images(id, '', random_image)
            #     try:
            #         os.remove('data/images/' + random_image)
            #     except FileNotFoundError:
            #         print(
            #             'изображение для удаления не найдено(что странно).')
            #     k += 1
            # elif message == '!инфо':
            #     f.send_message(id, f.open_txt('info.txt'))
            #     k += 1
            # else:
            #     response = vk.users.get(user_ids=id, fields='first_name,last_name')

            #     user_info = response[0]
            #     first_name = user_info['first_name']

            #     f.send_message(
            #         id, f'{first_name}, к сожалению, я всего лишь бот')
            #     k += 1

            # if k == 1:
            #     continue


if __name__ == '__main__':
    main()
