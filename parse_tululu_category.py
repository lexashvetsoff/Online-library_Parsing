import requests
import os
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, urlsplit
import json

BASE_URL = 'https://tululu.org'
PARSE_URL = 'https://tululu.org/l55/'
DOWNLOAD_URL = 'https://tululu.org/txt.php'


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def get_book_id(url):
    return sanitize_filename(urlsplit(url).path)[1:]


def parse_book_urls():
    books_url = []

    for page in range(1, 5):
        url = f'{PARSE_URL}{page}/'
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'lxml')

        book_objects = soup.find_all('table', class_='d_book')
        for book_obj in book_objects:
            books_url.append(urljoin(BASE_URL, book_obj.find('a')['href']))

    return books_url


def download_image(image_url, folder='images/'):
    """Функция для скачивания картинок"""
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)

    response = requests.get(image_url)
    response.raise_for_status()
    check_for_redirect(response)

    split_url = urlsplit(image_url)
    valid_filename = sanitize_filename(split_url.path)
    valid_folder = sanitize_filename(folder)

    filepath = os.path.join(valid_folder, valid_filename)
    with open(filepath, 'wb') as file:
        file.write(response.content)
    
    return filepath


def download_txt(url, book_id, title, folder='books/'):
    """Функция для скачивания текстовых файлов."""

    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)

    payload = {"id": book_id}
    response = requests.get(url, params=payload)
    response.raise_for_status()

    check_for_redirect(response)

    valid_filename = f'{sanitize_filename(title)}.txt'
    valid_folder = sanitize_filename(folder)

    filepath = os.path.join(valid_folder, valid_filename)
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(response.text)
    
    return filepath


def parse_book_page(book_url):
    response = requests.get(book_url)
    response.raise_for_status()
    check_for_redirect(response)
    soup = BeautifulSoup(response.text, 'lxml')
    
    book_title = soup.find('div', id='content').find('h1')
    text = book_title.text.split('::')
    title, author = text[0].strip(), text[1].strip()

    genres_obj = soup.find('span', class_='d_book').find_all('a')
    genres = [genre.text for genre in genres_obj]

    comments_obj = soup.find('div', id='content').find_all('span', class_='black')
    comments = [comment.text for comment in comments_obj]

    book_image = soup.find('div', class_='bookimage').find('img')
    image_url = urljoin(BASE_URL, book_image['src'])

    img_src = download_image(image_url)
    book_path = download_txt(DOWNLOAD_URL, get_book_id(book_url), title)

    data_page = {
        'Название': title,
        'Автор': author,
        'img_src': img_src,
        'book_path': book_path,
        'Жанр': genres,
        'Коментарии': comments,
        'image_url': image_url
    }
    return data_page


def main():
    data_books = []
    book_urls = parse_book_urls()

    i = 1
    for book_url in book_urls:
        print(i)
        try:
            data_books.append(parse_book_page(book_url))
        except requests.HTTPError:
            print('Такой книги нет!')
        i += 1
    
    with open("data_books.json", "w", encoding='utf8') as file:
        json.dump(data_books, file, ensure_ascii=False)


if __name__ == '__main__':
    main()