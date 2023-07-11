import logging
from tg_api import send_message

token = '6075472551:AAHp_A6aPaJzBMR9W-ekgHwkE20feWzt3tc'
chat_id = -820642556


def send_log_line(message):
    send_message(token, chat_id, message)
