import aiohttp
import asyncio
from bs4 import BeautifulSoup
from settings import *
import re
import time
from tqdm import tqdm

start_time = time.time()

# RegEx паттерны для нахождения ссылки на скачивание
patterns = [r'"url":"https://i\.pinimg\.com[^"]+\.gif"',
            r'"url":"https://v1\.pinimg\.com[^"]+\.mp4"',
            r'"url":"https://i\.pinimg\.com[^"]+\.jpg"',]

# ссылки на посты, которые нужно открыть
with open(primary_save_file, 'r') as f1, open(secondary_save_file, 'r') as f2:
    urls1 = [line.strip() for line in f1]
    urls2 = [line.strip() for line in f2]
    urls = urls1 + urls2
print('Открываем', len(urls), 'постов')

# куда сохранятся ссылки на скачивание
with open(download_links, 'r', encoding='utf-8') as f:
    download_arr = [line.strip() for line in f]

print('Сбор ссылок на скачивание')


async def fetch_url(session, url):
    try:
        async with session.get(url) as response:
            # получить html разметку страницы
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')

            # найти элемент, в котором ссылки
            script_element = soup.find('script', {'data-relay-response': 'true'})
            script_content = script_element.string if script_element else ''

            # вытащить из найденного элемента ссылку на файл
            download_url = ''
            for pattern in patterns:
                match = re.findall(pattern, script_content)
                if match:
                    # print(match)
                    download_url = match[0][7:-1]
                    break

            if download_url:
                download_arr.append(download_url)

    except aiohttp.ClientError as e:
        print('ошибка', url)
        print(e)


async def main():
    length = len(urls)
    step = 1024  # по столько запросов за раз
    # левая и правая граница скользящего окна
    last_step = 0
    next_step = step

    # собирать пока не закончится список
    while True:
        async with aiohttp.ClientSession() as session:
            tasks = [fetch_url(session, url) for url in urls[last_step:next_step]]
            last_step += step
            next_step += step
            if tasks:
                await asyncio.gather(*tasks)
                if length <= last_step:  # если это последний цикл запросов
                    last_step = length
                print(f'Собрано {last_step} из {length}')

            else:
                break


asyncio.run(main())

# сохранить
with open(download_links, 'w', encoding='utf-8') as f:
    for i in set(download_arr):
        print(i, file=f)

print('\nГотово, сохранено', len(set(download_arr)), 'ссылок')
print("%s sec" % round(time.time() - start_time))
