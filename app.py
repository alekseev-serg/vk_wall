import requests
import time
import os
import re

BASE_DIR = os.path.dirname(__file__)
VERSION = '5.110'
GROUP_LIST = []
BAD_SYMBOL = ['/', '|']

with open("token.txt") as f:
    ACCESS_TOKEN = f.read().strip()


def get_group_list():
    group_list = []
    with open('group_list.txt', 'r') as file:
        for item in file:
            group_id = re.findall(r"\d+", item)
            group_list.append(group_id[0])

    return group_list


def group_name(group):
    try:
        response = requests.get('https://api.vk.com/method/groups.getById',
                                params={
                                    'access_token': ACCESS_TOKEN,
                                    'v': VERSION,
                                    'group_id': group,
                                })

        name = response.json()['response'][0]['name']
        for item in BAD_SYMBOL:
            if item in name:
                name = name.replace(item, '-')
    except:
        name = 'group {} error'.format(group)

    return name


def get_posts(group):
    posts = []
    try:
        response = requests.get('https://api.vk.com/method/wall.get',
                                params={
                                    'access_token': ACCESS_TOKEN,
                                    'v': VERSION,
                                    'owner_id': '-' + group,
                                    'count': 20,
                                })

        data = response.json()['response']['items']
        posts.extend(data)
    except:
        posts = 'No DATA'

    return posts


def get_post_text(posts, group_id, group_name):
    os.mkdir(BASE_DIR + '/out/' + group_name + '-' + group_id)
    with open('out/' + group_name + '-' + group_id + '/posts.txt', 'w') as file:
        for post in posts:
            try:
                url = 'https://vk.com/wall-' + group_id + '_' + str(post['id'])
                file.write(url + '\n')
                if post['text'] == '':
                    post['text'] = 'В этом посте изображение'
                    file.write(post['text'] + '\n\n')
                else:
                    file.write(post['text'] + '\n\n')
            except:
                file.write('в сообщении присутствует недопустимый символ либо другая ошибка \n\n')


def get_comments(posts, group_id, group_name):
    for post in posts:
        with open('out/' + group_name + '-' + group_id + '/wall-' + group_id + '_' + str(post['id']) + '.txt', 'w',
                  encoding="utf-8") as file:
            url = 'https://vk.com/wall-' + group_id + '_' + str(post['id']) + '\n\n'
            file.write(url)
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
            time.sleep(0.5)

            for comment in comments:
                try:
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
                            file.write('https://vk.com/id' + str(comment['from_id']) + ' написал(а):\n'
                                       + item['text'] + '\n\n')

                except:
                    file.write('комментарий удалён\n\n')
                    print(f"Some error in comments in {group_name} - https://vk.com/wall-{group_id}_{post['id']}")


def main():
    time.sleep(50400)
    GROUP_LIST.extend(get_group_list())

    for group in GROUP_LIST:
        name = group_name(group)  # Получение названия группы
        print(f'Начинаю сбор информации в группе {name}-club{group}')
        posts = get_posts(group)  # Получение списка постов
        get_post_text(posts, group, name)  # Получение текста постов и запись в файл out\group_name(group)\post.txt
        get_comments(posts, group, name)  # Получение всех комментариев к каждому посту
        print(f'Сбор информации в группе {name} закончен')
        print("-------------------------------------------------------")


if __name__ == '__main__':
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))
