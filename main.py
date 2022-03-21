import requests
import os
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin

BASE_URL = 'https://tululu.org'
BOOK_URL = 'https://tululu.org/b'
DOWNLOAD_URL = 'https://tululu.org/txt.php'


def send_request(url, payload={}):
    response = requests.get(url, params=payload)
    response.raise_for_status()

    return response


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def get_soup_html(url):
    response = send_request(url)
    return BeautifulSoup(response.text, 'lxml')


def get_book_image(id):
    url = f'{BOOK_URL}{id}/'

    soup = get_soup_html(url)
    if soup.find('div', class_='bookimage'):
        book_image = soup.find('div', class_='bookimage').find('img')
        return urljoin(BASE_URL, book_image['src'])


def get_book_title(id):
    url = f'{BOOK_URL}{id}/'

    soup = get_soup_html(url)
    if soup.find('div', id='content'):
        book_title = soup.find('div', id='content').find('h1')
        text = book_title.text.split('::')
        return text[0].strip()


def download_txt(url, id, folder='books/'):
    """Функция для скачивания текстовых файлов."""

    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)

    payload = {"id": id}

    response = send_request(url, payload=payload)

    title = get_book_title(id)

    valid_filename = f'{id}.{sanitize_filename(title)}.txt'
    valid_folder = sanitize_filename(folder)

    try:
        check_for_redirect(response)
        filepath = os.path.join(valid_folder, valid_filename)
        with open(filepath, 'wb') as file:
            file.write(response.content)
    except requests.HTTPError:
        print('Такой книги нет!')


for i in range(1, 11):
    # download_txt(DOWNLOAD_URL, i)
    print(get_book_image(i))
