import requests
import os
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def get_book_title(id):
    url = f'https://tululu.org/b{id}/'

    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'lxml')
    if soup.find('div', id='content'):
        book_title = soup.find('div', id='content').find('h1')
        text = book_title.text.split('::')
        return text[0].strip()


def download_txt(url, id, folder='books/'):
    """Функция для скачивания текстовых файлов."""

    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)

    payload = {"id": id}

    response = requests.get(url, params=payload)
    response.raise_for_status()

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


url = 'https://tululu.org/txt.php'

for i in range(1, 11):
    download_txt(url, i)
