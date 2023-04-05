import logging
from time import time, sleep

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from acr_cloud import send_acr, extract_data
from avtoradio import load_stream, get_sum, BASE_URL, STATUS_ATTR
from tg_api import send_message

API_TOKEN = '5382856856:AAFbWXdhdxD1iNisi0_mcxJ_j-odFkzqu68'

WAITING_TIME = 60

CHAT_ID_TEST_CHAT = -770354772
CHAT_ID_OPEN_CHAT = -1001631831573
CHAT_ID_CLOSED_CHAT = -1001728313930

avtoradio = 'Авторадио'
superfinal = 'Игра «Много денег». Суперфинал'
utro = 'Утреннее Шоу «Поехали»'

FILENAME_STREAM = 'stream.mp3'


def init_browser():
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return browser


def save_stream_to_mp3(stream, filename):
    logging.info('Запись в файл')
    with open(filename, 'wb') as f:
        f.write(stream)


def wait_status(status, obj, waiting):
    t1 = time()
    t2 = t1
    while obj.text == status:
        t2 = time()
        if t2 - t1 >= waiting:
            break
    return t2 - t1


def final(artist, title):
    summ = get_sum()
    msg = (
        f'*Внимание!*\n'
        f'Близится игра «Много денег».\n'
        f'*Сумма в банке - {summ}р.*\n'
        f'Исполнитель - *{artist}*\n'
        f'Название песни - *{title}*\n'
        f'Желаем удачи!'
    )
    send_message(API_TOKEN, CHAT_ID_TEST_CHAT, msg, 'Markdown')
    # send_audio(filename, API_TOKEN, CHAT_ID_TEST_CHAT, f'{artist} - {title}')


def prepare_avtoradio(status, etalon=avtoradio):
    if wait_status(etalon, status, WAITING_TIME) < WAITING_TIME:
        return

    data = []
    for _ in range(0, 3):
        if status.text != etalon:
            return
        stream = load_stream(8)
        save_stream_to_mp3(stream, FILENAME_STREAM)
        result = send_acr(FILENAME_STREAM)
        logging.info(result)
        if result.get('status').get('msg') == 'Success':
            data.append(extract_data(result))
        if len(data) >= 2:
            if result.get('status').get('msg') != 'Success':
                return
            if data[-1] == data[-2]:
                final(*data[-1])
                wait_status(etalon, status, 600)
        sleep(10)


def prepare_superfinal(status):
    return status


def prepare_utro(status):
    prepare_avtoradio(status, utro)
    return status


def task(browser):
    status = browser.find_element(By.CLASS_NAME, STATUS_ATTR)
    prev = ''
    while True:
        current = status.text
        if current == avtoradio:
            logging.info(f'-------> {current}')
            prepare_avtoradio(status)
        elif current == superfinal:
            logging.info(f'-------> {current}')
            prepare_superfinal(status)
        elif current == utro:
            logging.info(f'-------> {current}')
            prepare_utro(status)
        elif prev != current:
            logging.info(f'         {current}')
            prev = current


def main():
    file_log = logging.FileHandler('info.log')
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
            logging.info('Переход на страницу авторадио')
            browser.get(BASE_URL)
            break
        except TimeoutException as err:
            logging.info(f'{err}')
            browser.close()

    logging.info('Запуск цикла')
    while True:
        try:
            task(browser)
            sleep(1)
        except Exception as err:
            print(err)
            logging.info(err)
        except KeyboardInterrupt:
            logging.info('Завершение работы')
            browser.close()


if __name__ == '__main__':
    main()
