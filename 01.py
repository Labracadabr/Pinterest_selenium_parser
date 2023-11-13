from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from settings import *

main_url = 'https://pinterest.com/ideas/'
options = webdriver.ChromeOptions()

if not show_browser:  # отображать ли браузер во время работы
    options.add_argument('--headless')


def search_request(req):
    # найти поисковую строку и нажать
    bar = browser.find_element(By.XPATH,
                               '//*[@id="__PWS_ROOT__"]/div/div[1]/div/div[1]/div/div[2]/div/div/form/div/div[1]/div[2]/div/input')
    bar.clear()
    bar.send_keys(req + '\n')  # ввод запроса, '\n' имитирует нажатие Enter
    print('запрос:', req)


def scroll(y):
    browser.execute_script(f"window.scrollBy(0,{y})")
    # print('scroll:', y, 'px')


def find():
    # поиск по пути элемента (xpath)
    div = 0
    while True:
        try:
            div += 1

            # проверка подходит ли тип файла
            path = f'//*[@id="mweb-unauth-container"]/div/div[2]/div[2]/div/div/div/div[1]/div[{div}]/div/div/div/div/div[1]/a/div/div'
            elem_type = pin_type(browser, path)
            if not elem_type:
                break
            if elem_type not in desired_types:
                continue

            # поиск ссылки на пост
            xpath = f'//*[@id="mweb-unauth-container"]/div/div[2]/div[2]/div/div/div/div[1]/div[{div}]/div/div/div/div/div[1]/a'
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

    # перебор каждого поискового запроса
    for request in search_requests:
        found_links = []
        browser.get(main_url)  # открыть сайт
        time.sleep(1)
        search_request(request)  # вбить поиск
        time.sleep(2)
        heights = [x for x in range(4)]  # список последних высот страницы

        # скролим до упора
        while True:
            time.sleep(1)
            find()  # поиск нужных элементов
            print('\rнайдено:', len(found_links), end='')
            scroll(y=4000)  # скролл вниз

            # замерить высоту страницы
            height = browser.execute_script("return document.body.scrollHeight")
            heights.pop(0)
            heights.append(height)

            # если высота не меняется 4 скрола подряд - скролить больше некуда
            if len(set(heights)) == 1:
                print("\nДостигнут конец страницы")
                break

        print('Сохранение ссылок')
        old_len, new_len = save(primary_save_file, found_links)

        print_status(found_links=found_links, new_len=new_len, old_len=old_len)
