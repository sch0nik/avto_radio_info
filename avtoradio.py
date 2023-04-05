import logging
from time import time

import requests
from bs4 import BeautifulSoup

BASE_URL = 'https://www.avtoradio.ru/'
MONEY_URL = 'https://www.avtoradio.ru/money/'
STREAM_URL = 'http://ic7.101.ru:8000/v3_1?139a7a02'
STATUS_ATTR = 'TitleSongAir'


def load_stream(duration=50):
    logging.info('Загрузка потока')
    t1 = time()
    stream_byte = b''
    stream = requests.get(STREAM_URL, stream=True)
    if stream.status_code == 200:
        for block in stream.iter_content(1024):
            t2 = time()
            stream_byte += block
            if t2 - t1 > duration:
                return stream_byte
    return False


def get_sum():
    r = requests.get(MONEY_URL)
    if r.status_code == 200:
        result = BeautifulSoup(r.text, 'html.parser')
        result = result.select('.summa')[0]
        result = result.text.strip()
    else:
        result = 'Неизвестно'
    return result
