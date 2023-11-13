import aiohttp
import asyncio
import os
from settings import download_links
import time
start_time = time.time()


# где сохраняются файлы
save_folder = 'save_folder'
if not os.path.exists(save_folder):
    os.makedirs(save_folder)  # создается папка

# ссылки, по которым будем скачивать файлы
with open(download_links, 'r', encoding='utf-8') as f:
    links_arr = list(set(line.strip() for line in f))

# по названиям отфильтровать то, что еще не скачано (исключить то, что уже находится в save_folder)
download_filtered = [link for link in links_arr if link.split('/')[-1] not in os.listdir(save_folder)]

# убедиться, что список не пуст
if not download_filtered:
    print('Скачивать нечего')
    exit()
print('Скачивание')
length = len(download_filtered)


# скачивание по ссылкам
async def download_from_link(session, link):
    extension = link.split('.')[-1]
    name = link.split('/')[-1].split('.')[0]
    # print(f'{name}.{extension} downloading')

    try:
        async with session.get(url=link) as response:
            filename = os.path.join(save_folder, f'{name}.{extension}')
            # создать файл
            with open(filename, 'wb') as media:
                while True:  # скачивание чанками
                    chunk = await response.content.read(100000)
                    if not chunk:
                        break
                    media.write(chunk)
    # в случае ошибки написать ссылку и ошибку
    except Exception as e:
        print('ошибка', link)
        print(e)


async def main():
    step = 16  # максимальное число параллельных загрузок
    # левая и правая граница скользящего окна
    last_step = 0
    next_step = step

    # скачивать пока не закончится список
    while True:
        async with aiohttp.ClientSession() as session:
            tasks = [download_from_link(session, link) for link in download_filtered[last_step:next_step]]
            last_step += step
            next_step += step
            if tasks:
                await asyncio.gather(*tasks)
                if length <= last_step:  # если это последний цикл скачивания
                    last_step = length
                print(f'Скачано {last_step} из {length}')
            else:
                break


asyncio.run(main())

print('\nГотово')
print("%s sec" % round(time.time() - start_time))
