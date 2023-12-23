import aiohttp
import asyncio
from bs4 import BeautifulSoup
from settings import *
import re
import time
import platform
if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
start_time = time.time()


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
                    download_url = match[0][7:-1]
                    break

            # сохранить найденную ссылку
            if download_url:
                download_arr.append(download_url)

    except aiohttp.ClientError as e:
        print('ошибка', url)
        print(e)


async def main():
    length = len(urls)
    step = 1024  # по столько запросов за раз

    # скачивать пока не закончится список
    for i in range(0, length, step):
        async with aiohttp.ClientSession() as session:
            tasks = [fetch_url(session, url) for url in urls[i:i+step]]
            await asyncio.gather(*tasks, return_exceptions=True)

        print(f'Открыто {min(i+step, length)} из {length}')

asyncio.run(main())

# сохранить
with open(download_links, 'w', encoding='utf-8') as f:
    for i in set(download_arr):
        print(i, file=f)

print('\nГотово, сохранено', len(set(download_arr)), 'ссылок')
print("%s sec" % round(time.time() - start_time))
