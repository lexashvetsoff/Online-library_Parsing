import requests
import os
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, urlsplit
import json
import argparse

BASE_URL = 'https://tululu.org'
PARSE_URL = 'https://tululu.org/l55/'
DOWNLOAD_URL = 'https://tululu.org/txt.php'


def get_last_page(url):
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'lxml')
    page_selector = 'p.center a.npage'
    link_pages = soup.select(page_selector)
    last_link = link_pages.pop()
    return int(last_link.text)


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--start_page', default=1, type=int)
    parser.add_argument('--end_page', default=get_last_page(PARSE_URL), type=int)
    parser.add_argument('--dest_folder_img', default='images/', type=str)
    parser.add_argument('--dest_folder_txt', default='books/', type=str)
    parser.add_argument('--skip_imgs', default=False, type=bool)
    parser.add_argument('--skip_txt', default=False, type=bool)
    parser.add_argument('--json_path', default='books_data.json', type=str)

    return parser


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def parse_book_urls(start_page, end_page):
    books_url = []
    for page in range(start_page, end_page + 1):
        url = f'{PARSE_URL}{page}/'
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'lxml')

        book_selector = 'table.d_book'
        book_objects = soup.select(book_selector)
        for book_obj in book_objects:
            link_selector = 'a'
            books_url.append(urljoin(BASE_URL, book_obj.select_one(link_selector)['href']))

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

    title_selector = '#content h1'
    book_title = soup.select_one(title_selector)
    text = book_title.text.split('::')
    title, author = text

    genres_selector = 'span.d_book a'
    genres_obj = soup.select(genres_selector)
    genres = [genre.text for genre in genres_obj]

    comments_selector = '#content span.black'
    comments_obj = soup.select(comments_selector)
    comments = [comment.text for comment in comments_obj]

    img_selector = '.bookimage img'
    book_image = soup.select_one(img_selector)
    image_url = urljoin(BASE_URL, book_image['src'])

    data_page = {
        'Название': title.strip(),
        'Автор': author.strip(),
        'Жанр': genres,
        'Коментарии': comments,
        'image_url': image_url
    }
    return data_page


def main():
    parser = create_parser()
    args = parser.parse_args()

    books_data = []
    book_urls = parse_book_urls(args.start_page, args.end_page)

    for book_url in book_urls:
        try:
            data = parse_book_page(book_url)

            data['img_src'] = 'Не скачивалась' if args.skip_imgs else download_image(data['image_url'], folder=args.dest_folder_img)
            book_id = sanitize_filename(urlsplit(book_url).path)[1:]
            data['book_path'] = 'Не скачивалась' if args.skip_txt else download_txt(DOWNLOAD_URL, book_id, data['Название'], folder=args.dest_folder_txt)

            books_data.append(data)
        except requests.HTTPError:
            print('Такой книги нет!')

    with open(args.json_path, 'w', encoding='utf8') as file:
        json.dump(books_data, file, ensure_ascii=False)


if __name__ == '__main__':
    main()
