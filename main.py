from vkbot import VKBot
import os
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    admin_ids = list(map(int, os.getenv('ADMIN_IDS').split(',')))
    trusted_ids = list(map(int, os.getenv('TRUSTED_IDS').split(',')))
    bot = VKBot(os.getenv('TOKEN'), os.getenv('YADISK_TOKEN'), admin_ids, trusted_ids)
    bot.listen()
