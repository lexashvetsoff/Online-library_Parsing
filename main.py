import requests
import os
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename, validate_filename


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def download_txt(url, id, filename, folder='books/'):
    """Функция для скачивания текстовых файлов.
    Args:
        url (str): Cсылка на текст, который хочется скачать.
        id (int): id книги которую скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)

    payload = {"id": id}

    response = requests.get(url, params=payload)
    response.raise_for_status()

    validate_filename = f'{sanitize_filename(filename)}.txt'
    validate_folder = sanitize_filename(folder)

    try:
        check_for_redirect(response)
        filepath = os.path.join(validate_folder, validate_filename)
        print(filepath)
        with open(filepath, 'wb') as file:
            file.write(response.content)
    except requests.HTTPError:
        print('Такой книги нет!')


book_url = 'https://tululu.org/b1/'
response = requests.get(book_url)
response.raise_for_status()

soup = BeautifulSoup(response.text, 'lxml')
book_title = soup.find('div', id='content').find('h1')
text = book_title.text.split('::')
title, author = text[0].strip(), text[1].strip()
# print(f'Название: {title}')
# print(f'Автор: {author}')
download_txt('https://tululu.org/txt.php', 1, title)

# directory_name = 'books'
# if not os.path.exists(directory_name):
#     os.makedirs(directory_name, exist_ok=True)

# url = 'https://tululu.org/txt.php'

# for i in range(1, 11):
#     payload = {"id": i}

#     response = requests.get(url, params=payload)
#     response.raise_for_status()

#     try:
#         check_for_redirect(response)
#         filename = f'books/id{i}.txt'
#         with open(filename, 'wb') as file:
#             file.write(response.content)
#     except requests.HTTPError:
#         print('Такой книги нет!')