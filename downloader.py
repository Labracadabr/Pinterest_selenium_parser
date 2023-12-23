import aiohttp
import asyncio
import os
from settings import download_links, folder
import time
import platform
if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
start_time = time.time()


# где сохраняются файлы
save_folder = f'{folder}/save_folder'
if not os.path.exists(save_folder):
    os.makedirs(save_folder)  # создается папка

print('Чтение')
# ссылки, по которым будем скачивать файлы
with open(download_links, 'r', encoding='utf-8') as f:
    already_saved = os.listdir(save_folder)  # что уже скачано
    # по названиям отфильтровать то, что еще не скачано (исключить то, что уже находится в save_folder)
    download_list = [line.strip() for line in f if line.strip().split('/')[-1] not in already_saved]

# убедиться, что список не пуст
if not download_list:
    exit('Скачивать нечего')
length = len(download_list)
print('Скачивание', length, 'файлов')


# узнать размер папки
def get_folder_size(folder_path):
    # измерить каждый файл в папке
    files = os.listdir(folder_path)
    total_size = sum(os.path.getsize(os.path.join(folder_path, filename)) for filename in files)

    # конвертация байтов в Гб
    total_size_gb = round(total_size / (1024 ** 3), 3)
    return total_size_gb


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
                    chunk = await response.content.read(1024**2)
                    if not chunk:
                        break
                    media.write(chunk)
    # в случае ошибки написать ссылку и ошибку
    except Exception as e:
        print('ошибка', link)
        print(e)


async def main():
    step = 32  # максимальное число параллельных загрузок. можно понизить, если возникают ошибки payload

    # скачивать пока не закончится список
    for i in range(0, length, step):
        async with aiohttp.ClientSession() as session:
            tasks = [download_from_link(session, link) for link in download_list[i:i+step]]
            await asyncio.gather(*tasks, return_exceptions=True)

        gb = get_folder_size(save_folder)
        print(f'Скачано {min(i+step, length)} из {length}:', gb, 'GB')


asyncio.run(main())

print('\nГотово')
print("%s sec" % round(time.time() - start_time))
