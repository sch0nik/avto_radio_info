from pprint import pprint
import time
from datetime import datetime


def start_game(filename):
    with open(filename, 'r') as f:
        text = f.readlines()

    result = []
    for index, line in enumerate(text[:-1]):
        if 'Игра «Много денег»' in line:
            result.append(line)
        if 'Утреннее Шоу «Поехали»' in line:
            result.append(line)
        if 'Вечернее шоу «Мурзилки LIVE»' in line:
            result.append(line)

    return result


def get_time(line):
    return datetime.strptime(line[:17], '%y.%m.%d %H:%M:%S')


def long_time(log):
    for index, line in enumerate(log[:-1]):
        # if ' - ' in line or 'Реклама' in line or 'Новости' in line:
        #     continue
        if 'Игра «Много Денег»' not in line:
            continue
        t1 = get_time(line)
        t2 = get_time(log[index + 1])
        print(f'{t2 - t1} | {line}', end='')


def avtoradio(log):
    """Продолжительность статуса авторадио."""
    result = []
    for index, line in enumerate(log[:-1]):
        if 'Авторадио' in line:
            t1 = datetime.strptime(line[:17], '%y.%m.%d %H:%M:%S')
            t2 = datetime.strptime(log[index + 1][:17], '%y.%m.%d %H:%M:%S')
            result.append((t2 - t1).seconds)
            # result.append((str(t2 - t1), line, log[index + 1]))
    result = sorted(result, reverse=True)
    print(result)


def time_status(status, log):
    """Продолжительность статуса."""
    result = []
    for index, line in enumerate(log[:-1]):
        if status in line:
            t1 = datetime.strptime(line[:19], '%Y-%m-%d %H:%M:%S')
            t2 = datetime.strptime(log[index + 1][:19], '%Y-%m-%d %H:%M:%S')
            result.append((t2 - t1).seconds)
    return result


def all_statuses(log):
    """Все виды статусов, кроме песен."""
    log = map(lambda x: x[20:-1], log)
    result = set([item for item in log if ' - ' not in item])
    print(result)


def status_show(log):
    index = 0
    length = len(log)
    while True:
        if index >= length:
            break
        if 'шоу' in log[index] or 'Шоу' in log[index]:
            pprint(log[index: index + 10])
            index += 10
            pprint('=====================')
            continue
        index += 1


def num_status(log):
    t1 = datetime.strptime('22.08.31 23:06:57', '%y.%m.%d %H:%M:%S')
    result = []
    for line in log:
        if 'Авторадио' in line:
            t2 = get_time(line)
            result.append((t2 - t1).seconds)
            t1 = t2
    pprint(sorted(result))


def main():
    filename = ['temp/info3.log']
    result = []
    for i in filename:
        print(i)
        with open(i, 'r') as f:
            log = f.readlines()
        result.extend(time_status('Утреннее шоу «Поехали»', log))
    result.sort()
    print(result[:21])
    print(result[-20:])

    # num_status(log)
    # status_show(log)
    # all_statuses(log)
    # avtoradio(log)
    # long_time(log)


if __name__ == '__main__':
    main()
