from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from settings import *

# на этом этапе мы открываем каждую ссылку, добытую в предыдущем этапе, и собираем все похожие посты (related pins)
# чтобы повторно не открывать ссылки - открытые пишутся в файл done_file

options = webdriver.ChromeOptions()
if not show_browser:  # отображать ли браузер во время работы
    options.add_argument('--headless')

print('Загрузка')
# ссылки, которые нужно открыть
with open(primary_save_file, 'r', encoding='utf-8') as f:
    urls = [line.strip() for line in f]

# то, что уже открывалось - внести в список done_list
with open(done_file, 'r', encoding='utf-8') as f:
    done_list = [line.strip() for line in f]


def scroll(y):
    browser.execute_script(f"window.scrollBy(0,{y})")
    # print('scroll:', y, 'px')


def find(pin_id):
    # поиск по пути элемента (xpath)
    div = 0
    while True:
        try:
            # print('\rfound:', div, end='')
            div += 1
            # проверка подходит ли тип файла
            path = f'//*[@id="related-pins:{pin_id}"]/div/div[1]/div[{div}]/div/div/div/div/div[1]/a/div/div'
            elem_type = pin_type(browser, path)
            if not elem_type:
                break
            if elem_type not in desired_types:
                continue

            # поиск ссылки на пост
            xpath = f'//*[@id="related-pins:{pin_id}"]/div/div[1]/div[{div}]/div/div/div/div/div[1]/a'
            element = browser.find_element(By.XPATH, xpath)

            # вытащить из найденного элемента ссылку на пост
            href = element.get_attribute('href')
            found_links.append(href)

        except StaleElementReferenceException:  # если нет ссылки
            continue
        except NoSuchElementException:  # если больше ничего нет
            break


# открыть браузер
with webdriver.Chrome(options=options) as browser:
    length = len(urls)
    # перебор каждой ссылки
    for i, url in enumerate(urls, start=1):

        # если уже открывали - пропустить
        if url in done_list:
            continue

        print(url)
        print(f'url {i}/{length}')
        found_links = []
        pin_id = url.split('/')[-2]  # id поста
        browser.get(url)  # открыть пост
        time.sleep(1)
        heights = [x for x in range(4)]  # список последних высот страницы

        # скролим до упора
        while True:
            time.sleep(1)
            find(pin_id)  # поиск нужных элементов
            print('\rнайдено:', len(found_links), end='')
            scroll(y=4000)  # скролл вниз

            # замерить высоту страницы
            height = browser.execute_script("return document.body.scrollHeight")
            heights.pop(0)
            heights.append(height)

            # если высота не меняется 4 скрола подряд - скролить больше некуда
            if len(set(heights)) == 1:
                print("\nДостигнут конец страницы")

                # сохранить пройденную ссылку, чтобы больше не открывать
                done_list.append(url)
                with open(done_file, 'a', encoding='utf-8') as f:
                    print(url, file=f)
                break

        print('Сохранение')
        old_len, new_len = save(secondary_save_file, found_links)
        
        print_status(found_links=found_links, new_len=new_len, old_len=old_len)
