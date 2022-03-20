import datetime
import os
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
    }

    response = requests.get(url, params=payload)
    data = response.json()

    for index, data_list in enumerate(data):
        print(f"Скачивается изображение NASA [{index+1}/{len(data)}]")
        img_url = data_list['hdurl']
        extension = get_ext(img_url)
        filepath = f'images/NASA{index}{extension}'
        upload_img(img_url, filepath)


def get_image_earth():
    api_key = os.environ['API_KEY_NASA']
    url = "https://api.nasa.gov/EPIC/api/natural/images"
    payload = {
        "api_key": api_key
    }

    response = requests.get(url, params=payload)
    data = response.json()
    for index, metadata_image in enumerate(data):
        print(f"Скачивается изображение Earth[{index+1}/{len(data)}]")
        filepath = f'images/Earth{index}.png'
        image = metadata_image["image"]
        date = datetime.datetime.fromisoformat(metadata_image["date"])
        formatted_date = date.strftime("%Y/%m/%d")
        url = f"https://api.nasa.gov/EPIC/archive/natural/{formatted_date}/png/{image}.png"
        upload_img(url, filepath, payload=payload)


if __name__ == "__main__":
    load_dotenv()
    TOKEN = os.environ['TG_TOKEN']
    bot = telegram.Bot(token=TOKEN)
    # bot.send_message(text='Hi!', chat_id=-1001631391427)
    bot.send_photo(chat_id=-1001631391427, photo=open("images/NASA0..jpg", "rb"))
    
    # @NASAimg_bot

