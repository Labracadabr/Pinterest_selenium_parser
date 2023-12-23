from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from settings import *
options = webdriver.ChromeOptions()

if not show_browser:  # отображать ли браузер во время работы
    options.add_argument('--headless')


def scroll(y):
    browser.execute_script(f"window.scrollBy(0,{y})")
    # print('scroll:', y, 'px')


def find(request):
    # поиск по пути элемента (xpath)
    div = 0
    while True:
        try:
            div += 1

            # поиск ссылки на пост
            xpath = f'//*[@id="search:pins:{"-".join(request.split())}::---:"]/div/div[1]/div[{div}]/div/div/div/div/div[1]/a'
            element = browser.find_element(By.XPATH, xpath)

            # вытащить из найденного элемента ссылку на пост
            href = element.get_attribute('href')
            # print('href', href)
            found_links.append(href)

        except StaleElementReferenceException:  # если нет ссылки
            continue
        except NoSuchElementException:  # если больше ничего нет
            break


# открыть браузер
with webdriver.Chrome(options=options) as browser:

    # перебор каждого поискового запроса
    for search_request in search_requests:
        # открыть поисковую ссылку
        search_url = f'https://id.pinterest.com/search/pins/?q={"%20".join(search_request.split())}'
        print('search', search_url)
        time.sleep(1)
        browser.get(search_url)

        heights = [x for x in range(4)]  # список последних высот страницы
        found_links = []

        # скролим до упора
        while True:
            time.sleep(1)
            find(request=search_request)  # поиск нужных элементов
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
