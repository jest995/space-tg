import datetime
import logging
import os
import random
import time
from urllib.parse import urlparse

import requests
import telegram
from dotenv import load_dotenv


def upload_img(url, filepath, payload=""):
    directory = os.path.dirname(filepath)
    if not os.path.exists(directory):
        os.makedirs(directory)

    response = requests.get(url, params=payload)
    response.raise_for_status()

    with open(filepath, 'wb') as file:
        file.write(response.content)


def get_ext(url):
    parse_url = urlparse(url)
    extension = os.path.splitext(parse_url.path)
    return extension[1]


def get_images_nasa():
    api_key = os.environ['API_KEY_NASA']

    url = "https://api.nasa.gov/planetary/apod"
    payload = {
        "api_key": api_key,
        "count": 3
        "count": 10
    }

    response = requests.get(url, params=payload)
    response.raise_for_status()
    data = response.json()

    for index, data_list in enumerate(data):
        print(f"Скачивается изображение NASA [{index+1}/{len(data)}]")
        img_url = data_list['hdurl']
        logging.info(f"Скачивается изображение NASA [{index+1}/{len(data)}]")
        img_url = data_list['url']
        extension = get_ext(img_url)
        filepath = f'images/NASA{index}{extension}'
        upload_img(img_url, filepath)
        if extension:
            filepath = f'images/NASA{index}{extension}'
            upload_img(img_url, filepath)


def get_image_earth():
    api_key = os.environ['API_KEY_NASA']
    url = "https://api.nasa.gov/EPIC/api/natural/images"
    payload = {
        "api_key": api_key
    }

    response = requests.get(url, params=payload)
    response.raise_for_status()
    data = response.json()
    logging.info("Скачивается изображение Earth")
    filepath = f'images/Earth.png'
    image = data[0]["image"]
    date = datetime.datetime.fromisoformat(data[0]["date"])
    formatted_date = date.strftime("%Y/%m/%d")
    url = f"https://api.nasa.gov/EPIC/archive/natural/{formatted_date}/png/{image}.png"
    upload_img(url, filepath, payload=payload)

if __name__ == "__main__":
    logging.basicConfig(filename="info.log",
                        level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%d-%m-%y %H:%M:%S'
                        )
    logging.info("Start")
    load_dotenv()
    TOKEN = os.environ['TG_TOKEN']
    DELAY = int(os.environ['DELAY_POSTING'])
    CHAT_ID = int(os.environ['CHAT_ID'])
    os.makedirs('images/', exist_ok=True)
    bot = telegram.Bot(token=TOKEN)

    while True:
        if len(os.listdir('images')) == 0:
            logging.info("Изображений не найдено. Скачиваю")
            try:
                get_images_nasa()
                get_image_earth()
            except requests.exceptions.HTTPError as error:
                logging.exception("Exception occurred")
                time.sleep(10)
                continue

            logging.info("Скачал все изображения")

        images_list = os.listdir('images')
        image = random.choice(images_list)
        bot.send_photo(chat_id=CHAT_ID, photo=open(f"images/{image}", "rb"))
        os.unlink(f"images/{image}")
        logging.info("Старт паузы до отправки следующего сообщения в группу")
        time.sleep(DELAY)
