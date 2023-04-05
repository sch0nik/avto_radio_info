import base64
import hashlib
import hmac
import logging
import os
from time import time

import requests

# access_key = "dac36509002732b528e21dffdb2cfee4"
# access_secret = "w58IgTFQ7d4gshQQ8YkSjKgFvfPSEdBj4BuwPUCg"
access_secret = "lzoNQXueLhPpKpJQ1c5WBQNRhjb58rT2HhSaiORw"
access_key = "6ecd5ae53e9f6d6fa9dc36bb32ed0450"
requrl = "https://identify-eu-west-1.acrcloud.com/v1/identify"


def send_acr(filename):
    logging.info('Отправка в ACRCloud')
    http_method = "POST"
    http_uri = "/v1/identify"
    data_type = "audio"
    signature_version = "1"
    timestamp = time()
    string_to_sign = '\n'.join([http_method, http_uri, access_key, data_type, signature_version, str(timestamp)])
    sign = base64.b64encode(
        hmac.new(
            access_secret.encode('ascii'), string_to_sign.encode('ascii'), digestmod=hashlib.sha1
        ).digest()
    ).decode('ascii')
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
    music = result.get('metadata').get('music')
    music = music[1] if len(music) > 1 else music[0]
    artist = music.get('artists')
    artist = ', '.join([item['name'] for item in artist])
    title = music.get('title')
    return artist, title
