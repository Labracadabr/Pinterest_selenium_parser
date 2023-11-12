import aiohttp
import asyncio
from bs4 import BeautifulSoup
from settings import *
import re
import time

start_time = time.time()
session = None

# RegEx паттерны для нахождения ссылки на скачивание
patterns = [r'"url":"https://v1\.pinimg\.com[^"]+\.mp4"',
            r'"url":"https://i\.pinimg\.com[^"]+\.jpg"',
            r'"url":"https://i\.pinimg\.com[^"]+\.gif"',]

# ссылки на посты, которые нужно открыть
with open(primary_save_file, 'r') as f1, open(secondary_save_file, 'r') as f2:
    urls1 = [line.strip() for line in f1]
    urls2 = [line.strip() for line in f2]
    urls = urls1 + urls2

# ссылки, по которым будем скачивать файлы
with open(download_links, 'r', encoding='utf-8') as f:
    download_arr = [line.strip() for line in f]

print('Сбор ссылок на скачивание')


async def fetch_url(url):
    try:
        async with session.get(url) as response:
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            script_element = soup.find('script', {'data-relay-response': 'true'})
            script_content = script_element.string if script_element else ''

            # вытащить из найденного элемента ссылку на файл
            download_url = ''
            for pattern in patterns:
                match = re.findall(pattern, script_content)
                if match:
                    download_url = match[0][7:-1]
                    break

            if download_url:
                download_arr.append(download_url)
            else:
                print(url)
                raise Exception

    except aiohttp.ClientError as e:
        print(f"\nError fetching URL: {url}\n{e}")


async def main():
    global session
    session = aiohttp.ClientSession()

    tasks = [fetch_url(url) for url in urls]
    await asyncio.gather(*tasks)
    await session.close()


asyncio.run(main())

# сохранить
with open(download_links, 'w', encoding='utf-8') as f:
    for i in set(download_arr):
        print(i, file=f)

print('\nГотово, сохранено')
