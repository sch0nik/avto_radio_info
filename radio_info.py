import base64
import datetime
import hashlib
import hmac
import logging
import os
import time

import requests
import schedule
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

API_TOKEN = '5382856856:AAFbWXdhdxD1iNisi0_mcxJ_j-odFkzqu68'

url_web_app = 'http://91.77.168.64:8081/word-game/data'

BASE_URL = 'https://www.avtoradio.ru/'
MONEY_URL = 'https://www.avtoradio.ru/money/'
STREAM_URL = 'http://ic7.101.ru:8000/v3_1?139a7a02'

STATUS_ATTR = 'TitleSongAir'

# TIMINGS = ['00:09', '00:13']
TIMINGS = ['07:58', '09:58', '11:58', '14:58', '16:58', '18:58', '20:58']
# TIMINGS_OPEN_CHAT = ['08:15, '10:15', '12:15', '15:15', '17:15', '19:15']

WAITING_TIME = 12 * 60

CHAT_ID_TEST_CHAT = -770354772
CHAT_ID_OPEN_CHAT = -1001631831573
CHAT_ID_CLOSED_CHAT = -1001728313930

LAST_MSG = []

avtoradio = 'Авторадио'

access_key = "6ecd5ae53e9f6d6fa9dc36bb32ed0450"
# access_key = "dac36509002732b528e21dffdb2cfee4"
access_secret = "lzoNQXueLhPpKpJQ1c5WBQNRhjb58rT2HhSaiORw"
# access_secret = "w58IgTFQ7d4gshQQ8YkSjKgFvfPSEdBj4BuwPUCg"
requrl = "https://identify-eu-west-1.acrcloud.com/v1/identify"


def init_browser():
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return browser


def save_stream_to_mp3(chain, filename):
    with open(filename, 'wb') as f:
        for item in chain:
            f.write(item)


def load_stream(url, duration=50):
    t1 = time.time()
    chain_stream = []
    stream = requests.get(url, stream=True)
    if stream.status_code == 200:
        for block in stream.iter_content(1024):
            t2 = time.time()
            chain_stream.append(block)
            if t2 - t1 > duration:
                return chain_stream
    return False


def send_message(token, chat_id, text, mode=None):
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    params = {
        'chat_id': chat_id,
        'text': text,
    }
    if mode:
        params['parse_mode'] = mode
    return requests.get(url, params=params)


def send_ACR(filename):
    http_method = "POST"
    http_uri = "/v1/identify"
    data_type = "audio"
    signature_version = "1"
    timestamp = time.time()
    string_to_sign = http_method + "\n" + http_uri + "\n" + access_key + "\n" + data_type + "\n" + signature_version + "\n" + str(
        timestamp)
    sign = base64.b64encode(hmac.new(access_secret.encode('ascii'), string_to_sign.encode('ascii'),
                                     digestmod=hashlib.sha1).digest()).decode('ascii')
    sample_bytes = os.path.getsize(filename)
    files = [('sample', (filename, open(filename, 'rb'), 'audio/mpeg'))]
    data = {'access_key': access_key,
            'sample_bytes': sample_bytes,
            'timestamp': str(timestamp),
            'signature': sign,
            'data_type': data_type,
            "signature_version": signature_version}
    r = requests.post(requrl, files=files, data=data)
    r.encoding = "utf-8"
    return r.json()


def extract_data(result):
    music = result.get('metadata').get('music')[0]
    artist = music.get('artists')
    artist = ', '.join([item['name'] for item in artist])
    title = music.get('title')
    return artist, title


def get_sum():
    r = requests.get(MONEY_URL)
    if r.status_code == 200:
        result = BeautifulSoup(r.text, 'html.parser')
        result = result.select('.summa')[0]
        result = result.text.strip()
    else:
        result = 'Неизвестно'
    return result


def task(browser):
    logging.info('===============Старт задачи===============')

    filename = 'stream.mp3'
    status = browser.find_element(By.CLASS_NAME, STATUS_ATTR)
    money = get_sum()
    result = {}

    t1 = time.time()
    while True:
        t2 = time.time()
        result = {}
        logging.info(f'Новый цикл')
        if t2 - t1 > WAITING_TIME:
            # LAST_MSG.append(None)
            logging.info('Задача завершена по продолжительности')
            return 0
        if t2 - t1 > 5 * 60 and ' - ' in status.text:
            logging.info('Задача завершена, появилась новая песня')
            return 0
        if status.text in ['Новости', 'Реклама']:
            logging.info('Статус новости или реклама')
            time.sleep(30)
            continue

        logging.info('Проверка статуса')
        if ' - ' not in status.text:
            t3 = time.time()
            s = status.text
            while True:
                t4 = time.time()
                if t4 - t3 > 30 or s != status.text:
                    break
            if t4 - t3 > 30:
                logging.info('Запоминание потока')
                stream = load_stream(STREAM_URL, 15)
                logging.info('Сохранение записи в mp3')
                save_stream_to_mp3(stream, filename)
                logging.info('Получение результата из ACRCloud')
                result = send_ACR(filename)
                logging.info(f'{result}')
        else:
            logging.info('Играет другая песня')
            time.sleep(30)
            continue

        if result.get('status').get('msg') == 'Success':
            logging.info('Распознана песня')
            break
        else:
            logging.info('Запись не распознана')
            time.sleep(30)
            continue

    artist, title = extract_data(result)

    # LAST_MSG.append((artist, title, money))
    msg = (
        f'*Внимание!*\n'
        f'Близится игра «Много денег».\n'
        f'*Сумма в банке - {money}р.*\n'
        f'Исполнитель - *{artist}*\n'
        f'Название песни - *{title}*\n'
        f'Желаем удачи!'
    )
    # logging.info(f'Отправка сообщения в закрытый чат')
    # send_message(API_TOKEN, CHAT_ID_CLOSED_CHAT, msg, 'Markdown')
    logging.info(f'Отправка сообщения в открытый чат')
    send_message(API_TOKEN, CHAT_ID_OPEN_CHAT, msg, 'Markdown')
    requests.get(url_web_app, params={'summ': money, 'artist': artist, 'title': title})
    # logging.info(f'Отправка сообщения в открытый чат')
    # send_message(API_TOKEN, CHAT_ID_TEST_CHAT, msg, 'Markdown')

    logging.info('Задача завершена')


def task_open_chat():
    money = get_sum()
    if LAST_MSG is None:
        return 0
    if LAST_MSG[-1] is None:
        return 0

    artist, title, old_money = LAST_MSG[-1]
    msg = (
        f'Информация о предыдущем розыгрыше игры «Много денег»\n'
        f'*Сумма в банке - {old_money}р.*\n'
        f'Исполнитель - *{artist}*\n'
        f'Название песни - *{title}*\n'
        f'*Сумма в банке на следующий розыгрыш - {money}*'
    )
    return send_message(API_TOKEN, CHAT_ID_OPEN_CHAT, msg, 'Markdown')


def main():
    file_log = logging.FileHandler('info1.log')
    console_log = logging.StreamHandler()
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s::%(levelname)s::%(message)s',
        handlers=(file_log, console_log)
    )
    logging.info('Старт скрипта')

    logging.info('Инициализация браузера')
    browser = init_browser()
    while True:
        try:
            browser.get(BASE_URL)
            break
        except TimeoutException as err:
            logging.info(f'{err}')
            browser.close()

    logging.info('Добавление задач в список')
    for t in TIMINGS:
        schedule.every().day.at(t).do(task, browser=browser)
    # for t in TIMINGS_OPEN_CHAT:
    #     schedule.every().day.at(t).do(task_open_chat)
    logging.info('Ожидание заданного времени')
    try:
        while True:
            try:
                schedule.run_pending()
                print(f'{datetime.datetime.now()}\r', end='')
                time.sleep(1)
            except Exception as err:
                print(err)
    except KeyboardInterrupt:
        logging.info('Завершение работы')
        browser.close()


if __name__ == '__main__':
    main()
