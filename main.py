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


def send_request(url, payload={}):
    response = requests.get(url, params=payload)
    response.raise_for_status()

    return response


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def get_soup_html(book_url, id):
    requests_url = f'{book_url}{id}/'
    response = send_request(requests_url)
    try:
        check_for_redirect(response)
        return BeautifulSoup(response.text, 'lxml')
    except requests.HTTPError:
            print('Такой книги нет!')


def get_books_genre(soup):
    genres = []
    if soup.find('span', class_='d_book'):
        genres_html = soup.find('span', class_='d_book').find_all('a')
        for genre in genres_html:
            genres.append(genre.text)
    return genres


def get_book_comments(soup):
    comments = []
    if soup.find('div', id='content'):
        comments_html = soup.find('div', id='content').find_all('span', class_='black')
        for comment in comments_html:
            comments.append(comment.text)
        return comments


def get_url_book_image(book_url, id):
    soup = get_soup_html(book_url, id)
    if soup:
        book_image = soup.find('div', class_='bookimage').find('img')
        return urljoin(BASE_URL, book_image['src'])


def get_book_title(soup):
    if soup:
        book_title = soup.find('div', id='content').find('h1')
        text = book_title.text.split('::')
        return text[0].strip(), text[1].strip()


def parse_book_page(soup):
    if soup:
        title, author = get_book_title(soup)
        genre = get_books_genre(soup)
        comments = get_book_comments(soup)

        parse_page = {
            'Название': title,
            'Автор': author,
            'Жанр': genre,
            'Коментарии': comments,
        }
        return parse_page


def download_image(id, folder='images/'):
    """Функция для скачивания картинок"""
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)

    url = get_url_book_image(BOOK_URL, id)

    if url:
        try:
            response = send_request(url)
            check_for_redirect(response)

            split_url = urlsplit(url)
            valid_filename = sanitize_filename(split_url.path)
            valid_folder = sanitize_filename(folder)

            filepath = os.path.join(valid_folder, valid_filename)
            filepath = os.path.join(valid_folder, valid_filename)
            with open(filepath, 'wb') as file:
                file.write(response.content)
        except requests.HTTPError:
            print('Такой книги нет!')


def download_txt(url, id, folder='books/'):
    """Функция для скачивания текстовых файлов."""

    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)

    payload = {"id": id}
    response = send_request(url, payload=payload)

    try:
        check_for_redirect(response)
        soup = get_soup_html(BOOK_URL, id)
        title, author = get_book_title(soup)

        valid_filename = f'{id}.{sanitize_filename(title)}.txt'
        valid_folder = sanitize_filename(folder)
        filepath = os.path.join(valid_folder, valid_filename)
        with open(filepath, 'wb') as file:
            file.write(response.content)
    except requests.HTTPError:
        print('Такой книги нет!')


def main():
    parser = create_parser()
    namespace = parser.parse_args()
    for i in range(namespace.start_id, namespace.end_id + 1):
        download_txt(DOWNLOAD_URL, i)
        download_image(i)
        soup = get_soup_html(BOOK_URL, i)
        print(i, parse_book_page(soup))
        print()


if __name__ == '__main__':
    main()
