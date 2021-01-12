from pathlib import Path
import datetime
import requests
import time
import os
import re
import getpass


def open_base_file(path):
    with open(path) as f:
        value = f.read().strip()

    return value


BASE_DIR = Path(__file__).parent
OUTPUT_FOLDER = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
VERSION = '5.110'
BAD_SYMBOL = ['/', '|']
POST_COUNT = 70
ACCESS_TOKEN = open_base_file(f'{BASE_DIR}/base/token.txt')
START_TIME = int(open_base_file(f'{BASE_DIR}/base/timestamp.txt'))
USER = getpass.getuser()
DICTIONARY = ['един', 'школ', 'мороз', 'мая']


def set_current_time():
    current_time = round(datetime.datetime.now().timestamp())
    with open('base/timestamp.txt', 'w') as file:
        file.write(str(current_time))

    return current_time


def remove_empty_file(path):
    dir_list = os.listdir(path)
    for folder in dir_list:
        for root, dirs, files in os.walk(path + folder):
            for file in files:
                path_way = os.path.join(root, file)
                if os.path.getsize(path_way) == 0:
                    os.remove(path_way)


def remove_empty_folder(path):
    dir_list = os.listdir(path)
    for folder in dir_list:
        if os.listdir(path + folder):
            continue
        else:
            os.rmdir(path + folder)


def get_group_list():
    """
    :return возвращает список уникальных ID групп ВК:
    """
    group_list = []
    with open('base/group_list.txt', 'r') as file:
        for item in file:
            group_id = re.findall(r"\d+", item)
            #  проверка на дубликаты в группе
            if group_id[0] not in group_list:
                group_list.append(group_id[0])
            else:
                continue

    return group_list


def get_group_name(group_id):
    try:
        response = requests.get('https://api.vk.com/method/groups.getById',
                                params={
                                    'access_token': ACCESS_TOKEN,
                                    'v': VERSION,
                                    'group_id': group_id,
                                })

        name = response.json()['response'][0]['name']
        for item in BAD_SYMBOL:
            if item in name:
                name = name.replace(item, '-')
    except:
        name = 'group {} error'.format(group_id)

    return name


def get_all_posts(group_id):
    """
    :param group_id:
    :return список постов в заданный промежуток времени:
    """
    posts = []
    finally_list = []

    try:
        response = requests.get('https://api.vk.com/method/wall.get',
                                params={
                                    'access_token': ACCESS_TOKEN,
                                    'v': VERSION,
                                    'owner_id': '-' + group_id,
                                    'count': POST_COUNT,
                                })

        data = response.json()['response']['items']
        posts.extend(data)
        for post in posts:
            if START_TIME < post['date'] < round(datetime.datetime.now().timestamp()):
                finally_list.append(post)

    except:
        finally_list = 'No DATA'

    return finally_list


def get_post_data(post, group_id, file):
    try:
        if post['text'] == '':
            post['text'] = 'В этом посте изображение'
            print(post['text'] + '\n\n')
        else:
            for item in DICTIONARY:
                if item in post['text']:
                    url = 'https://vk.com/wall-' + group_id + '_' + str(post['id'])
                    date = datetime.datetime.fromtimestamp(post['date'])

                    file.write(url + '\n')
                    file.write(date.strftime('%d-%m-%Y %H:%M') + '\n')
                    file.write(post['text'] + '\n\n')
    except:
        print('в сообщении присутствует недопустимый символ либо другая ошибка \n')


def get_comments(post, group_id, file):
    comments = []
    response = requests.get('https://api.vk.com/method/wall.getComments',
                            params={
                                'access_token': ACCESS_TOKEN,
                                'v': VERSION,
                                'owner_id': '-' + group_id,
                                'count': 100,
                                'post_id': post['id'],
                                'sort': 'asc',
                                'thread_items_count': '10'
                            })

    data = response.json()['response']['items']
    comments.extend(data)  # Список всех комментариев
    time.sleep(3)

    for comment in comments:
        try:
            for word in DICTIONARY:
                if word in comment['text']:
                    file.write(
                        'https://vk.com/id' + str(comment['from_id']) + ' написал(а):\n' + comment['text'] + '\n\n')

            if comment['thread']:
                response = requests.get('https://api.vk.com/method/wall.getComments',
                                        params={
                                            'access_token': ACCESS_TOKEN,
                                            'v': VERSION,
                                            'owner_id': '-' + group_id,
                                            'post_id': post['id'],
                                            'comment_id': comment['id'],
                                            'count': 100
                                        })
                data = response.json()['response']['items']
                for item in data:
                    for word in DICTIONARY:
                        if word in item['text']:
                            file.write('https://vk.com/id' + str(comment['from_id']) + ' написал(а):\n'
                                       + item['text'] + '\n\n')

        except:
            print('комментарий удалён\n')


def main():
    DAY = datetime.datetime.now().strftime('%d-%m-%Y')
    TIME = datetime.datetime.now().strftime('%H-%M')
    path_for_clear = str(OUTPUT_FOLDER) + '/VK_RESULT\\{}\\{}\\'.format(str(DAY), str(TIME))
    path_for_clear_files = str(OUTPUT_FOLDER) + '\\VK_RESULT\\{}\\'.format(str(DAY))
    count = 0
    for group_id in get_group_list():
        count += 1
        group_name = get_group_name(group_id)  # Получение названия группы

        dir_out = str(OUTPUT_FOLDER) + '\\VK_RESULT\\{}\\{}\\{}-{}'.format(DAY,
                                                                           TIME,
                                                                           group_name,
                                                                           group_id)  # путь до директории с результатом

        print(f'{count} - Начинаю сбор информации в группе {group_name}-club{group_id}')

        posts = get_all_posts(group_id)  # Получение списка постов за предыдущие сутки

        try:
            os.makedirs(dir_out)
        except:
            print(f'Директория {group_name} не может быть создана')

        for post in posts:
            with open(dir_out + '/wall-{}_{}.txt'.format(group_id, post['id']), 'w') as file:
                get_post_data(post, group_id, file)
                get_comments(post, group_id, file)  # Получение всех комментариев к каждому посту

    remove_empty_file(path_for_clear_files)  # удаляет нулевые файлы
    remove_empty_folder(path_for_clear)  # удаляем пустые папки в результатах


if __name__ == '__main__':
    while True:
        print(START_TIME)
        main()
        START_TIME = set_current_time()
        print(START_TIME)
        time.sleep(43200)
