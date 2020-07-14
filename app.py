import requests
import time
import os

BASE_DIR = os.path.dirname(__file__)
VERSION = '5.110'
GROUP_LIST = ['118193328', '95478897', '41670664', '35776429', '20801131', '87064207', '156022223', '134920716',
              '67743500', '59538394', '23917279', '38852926', '130028414', '93083717', '91532751', '34302728',
              '8718584', '152696483', '161982468', '66537290', '152511991', '67246679', '138519985', '31700592',
              '59124491', '37067542', '52651975', '95212422', '33079160', '47515083', '80183611', '31432289',
              '109065214', '176641622', '149573958', '41443169', '92750048', '183844571', '69317369', '156405711',
              '110854767', '164287640', '189058660', '129238676', '62797630', '21075514', '62910295', '27658788',
              '69702902', '74937737', '37584564', '132160688', '71291783', '17020012', '8683321', '185321877',
              '1148776', '179475789', '72394587', '181047672', '188213720', '60150642', '61276418', '20280490',
              '67626362', '96900405', '183608484', '70199689', '161132055', '60214007', '28840178', '152251763',
              '120404150', '66699150', '118981745', '118971633', '177191002', '165391365', '133121058', '136493730',
              '155498680', '1917801', '183876856', '69449846', '1184059', '107976918', '137647122', '67482091',
              '82992247', '64555574', '160518688', '74923018', '154786387', '59824267', '80389881', '13317058',
              '64692653', '150741160', '168189584', '2038124', '61360099', '123982096', '93140581', '92782460',
              '101397796', '2421211', '348775', '180787726', '58940754', '11530664', '61313387', '81481281', '73665298',
              '183949616', '15673679', '171788887', '62732437', '11312078', '63205740', '71835931', '52839807',
              '2305763', '7187719', '8820391', '64393030', '121511394', '38533949', '24330816', '37275788', '59108152',
              '56423657', '63893210', '85138724', '34208057', '132021284', '56142417', '127747096', '165697009',
              '191154827', '135610763', '43743994', '137230967', '193503525', '154606165', '6348962', '25622432',
              '70522864', '85353343', '107046496', '12173105', '12547193', '55296671', '121487452', '46178880',
              '95151216', '586418', '134682435', '103479933', '151903135', '185946112', '61363781', '157778393',
              '4833182', '89530630', '58296787', '176548372', '1805708', '186110674', '186042079', '155311161',
              '186110706', '174302361', '1337398']
BAD_SYMBOL = ['/', '|']

with open("token.txt") as f:
    ACCESS_TOKEN = f.read().strip()


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
