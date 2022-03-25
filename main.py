import requests
import os
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, urlsplit
import argparse

BASE_URL = 'https://tululu.org'
BOOK_URL = 'https://tululu.org/b'
DOWNLOAD_URL = 'https://tululu.org/txt.php'


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('start_id', default=1, type=int)
    parser.add_argument('end_id', default=10, type=int)

    return parser


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def parse_book_page(book_url, book_id):
    requests_url = f'{book_url}{book_id}/'
    response = requests.get(requests_url)
    response.raise_for_status()
    check_for_redirect(response)
    soup = BeautifulSoup(response.text, 'lxml')
    
    book_title = soup.find('div', id='content').find('h1')
    text = book_title.text.split('::')
    title, author = text[0].strip(), text[1].strip()

    genres_html = soup.find('span', class_='d_book').find_all('a')
    genres = [genre.text for genre in genres_html]

    comments_html = soup.find('div', id='content').find_all('span', class_='black')
    comments = [comment.text for comment in comments_html]

    book_image = soup.find('div', class_='bookimage').find('img')
    image_url = urljoin(BASE_URL, book_image['src'])

    parse_page = {
        'Название': title,
        'Автор': author,
        'Жанр': genres,
        'Коментарии': comments,
        'image_url': image_url
    }
    return parse_page


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
    filepath = os.path.join(valid_folder, valid_filename)
    with open(filepath, 'wb') as file:
        file.write(response.content)


def download_txt(url, book_id, title, folder='books/'):
    """Функция для скачивания текстовых файлов."""

    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)

    payload = {"id": book_id}
    response = requests.get(url, params=payload)
    response.raise_for_status()

    check_for_redirect(response)

    valid_filename = f'{book_id}.{sanitize_filename(title)}.txt'
    valid_folder = sanitize_filename(folder)
    filepath = os.path.join(valid_folder, valid_filename)
    with open(filepath, 'w') as file:
        file.write(response.text)


def main():
    parser = create_parser()
    args = parser.parse_args()
    for book_id in range(args.start_id, args.end_id + 1):
        try:
            parse_page = parse_book_page(BOOK_URL, book_id)
            download_txt(DOWNLOAD_URL, book_id, parse_page['Название'])
            download_image(parse_page['image_url'])
            print(book_id, parse_page)
            print()
        except requests.HTTPError:
            print('Такой книги нет!')


if __name__ == '__main__':
    main()
