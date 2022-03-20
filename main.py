import requests
import os
from bs4 import BeautifulSoup


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


book_url = 'https://tululu.org/b1/'
response = requests.get(book_url)
response.raise_for_status()

soup = BeautifulSoup(response.text, 'lxml')
book_title = soup.find('div', id='content').find('h1')
text = book_title.text.split('::')
title, author = text[0].strip(), text[1].strip()
print(f'Название: {title}')
print(f'Автор: {author}')
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