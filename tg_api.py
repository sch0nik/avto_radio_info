import logging

import requests


def send_message(token, chat_id, text, mode=None):
    """Отправить сообщение."""
    logging.info('Отправка сообщения')
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    params = {
        'chat_id': chat_id,
        'text': text,
    }
    if mode:
        params['parse_mode'] = mode
    return requests.get(url, params=params)


def send_audio(filename, token, chat_id, caption=None):
    """Отправить аудио."""
    logging.info('Отправка аудио')
    url = f'https://api.telegram.org/bot{token}/sendAudio'
    file = {'audio': open(filename, 'rb')}
    data = {'chat_id': chat_id}
    if caption:
        data['caption'] = caption
    return requests.post(url, files=file, data=data)
