import os
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


# поисковые запросы
search_requests: list = ['black cat', 'black dog']  # пример

# RegEx паттерны для нахождения ссылки на скачивание. Закомментить ненужные типы файлов. Применяется в файле 03
patterns: list = [
    r'"url":"https://i\.pinimg\.com[^"]+\.gif"',
    r'"url":"https://v1\.pinimg\.com[^"]+\.mp4"',
    r'"url":"https://i\.pinimg\.com/originals[^"]+\.jpg"',
    ]

# для каждой новой задачи переименовать папку folder
folder: str = 'project_1'

# Отображать ли браузер во время скрапинга. Можно скрыть, чтобы не мешало и не нагружать железо
show_browser: bool = False

# # # Дальше ничего не менять # # #

# файлы, где сохранятся ссылки
primary_save_file = f'{folder}/primary_pin_urls.csv'
secondary_save_file = f'{folder}/secondary_pin_urls.csv'
done_file = f'{folder}/done.csv'
download_links = f'{folder}/download.csv'

# создать файлы если их нет
os.makedirs(folder, exist_ok=True)
for file in (primary_save_file, secondary_save_file, done_file, download_links):
    if not os.path.isfile(file):
        with open(file, 'w', encoding='utf-8') as f:
            print('Создан файл', file)


# функции

# сохранить найденные ссылки и вернуть их число до и после сохранения
def save(file: str, data: list):
    # открыть сохраненные ссылки
    with open(file, 'r', encoding='utf-8') as f:
        arr = [line.strip() for line in f]
    old_len = len(arr)

    # добавить новые ссылки
    for link in data:
        if link not in arr:
            arr.append(link)
    new_len = len(arr)

    # сохранить
    with open(file, 'w', encoding='utf-8') as f:
        for i in arr:
            print(i, file=f)
    return old_len, new_len


# вывод в консоль статуса сбора
def print_status(found_links, new_len, old_len):
    offset = 15
    print('собрано ссылок'.ljust(offset), len(found_links))
    print('уникальных'.ljust(offset), len(set(found_links)))
    print('новых'.ljust(offset), new_len - old_len)
    print('было ссылок'.ljust(offset), old_len)
    print('стало'.ljust(offset), new_len)
    print('_' * offset)
    print()
