import os
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


# Какие файлы ищем. Есть 4 типа, закомментить ненужные
desired_types: list = [
    'video',
    'storyPin',  # storyPin - тоже видео
    'gif',
    'image',
]
# поисковые запросы
search_requests: list = ['3d animation video', '2d animation video', '3d animation gif', '2d animation gif', ]  # пример
# Дальше необязательно что-либо менять

# Отображать ли браузер во время скраппинга. Можно скрыть, чтобы не мешало и не нагружать железо
show_browser: bool = True

# где сохранятся ссылки
primary_save_file = 'primary_pin_urls.csv'
secondary_save_file = 'secondary_pin_urls.csv'
done_file = 'done.csv'
download_links = 'download.csv'

# создать файлы если их нет
for file in (primary_save_file, secondary_save_file, done_file, download_links):
    if not os.path.isfile(file):
        with open(file, 'w', encoding='utf-8') as f:
            print('Создан файл', file)


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


# найти тип файла (например pincard-gif-with-link)
def pin_type(browser, path: str):
    try:
        element = browser.find_element(By.XPATH, path)
        el_type = element.get_dom_attribute('data-test-id')
        el_type = el_type.split('-')[1]  # "pincard-gif-with-link" -> "gif"
    except AttributeError as e:
        el_type = 'bubble'  # если попался не пост, а блок рекомендаций
    except NoSuchElementException:
        return None  # если тип файла не найден, то вернуть None и прервать цикл
    # print(el_type)
    return el_type


def print_status(found_links, new_len, old_len):
    offset = 15
    print('собрано ссылок'.ljust(offset), len(found_links))
    print('уникальных'.ljust(offset), len(set(found_links)))
    print('новых'.ljust(offset), new_len - old_len)
    print('было ссылок'.ljust(offset), old_len)
    print('стало'.ljust(offset), new_len)
    print('_' * offset)
    print()
