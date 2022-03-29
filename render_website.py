from livereload import Server
from jinja2 import Environment, FileSystemLoader, select_autoescape
from more_itertools import chunked
from urllib.parse import quote
import json
import math
import os

with open('data_books.json', 'r', encoding="utf8") as file:
    data_books_json = file.read()
data_books = json.loads(data_books_json)

if os.sep == '\\':
    for book in data_books:
        book['img_src'] = book['img_src'].replace('\\', '/')
        book['book_path'] = book['book_path'].replace('\\', '/')
        book['book_path'] = quote(book['book_path'])


def on_reload():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')

    d_books = list(chunked(data_books, 20))
    
    for page_number, books in enumerate(d_books, 1):
        file_name = f'index{page_number}.html'
        folder = 'pages'

        all_pages = math.ceil(len(data_books) / 20)
        
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)

        rendered_page = template.render(
            books = books,
            all_pages = all_pages,
            current_page = page_number
        )

        file_path = os.path.join(folder, file_name)
        with open(file_path, 'w', encoding="utf8") as file:
            file.write(rendered_page)

    # if len(data_books) % 2 != 0:
    #     books = list(chunked(data_books, len(data_books) - 1))
    #     rendered_page = template.render(
    #         books = books[0]
    #     )
    # else:
    #     rendered_page = template.render(
    #         books = data_books
    #     )

    # with open('index.html', 'w', encoding="utf8") as file:
    #     file.write(rendered_page)

on_reload()

server = Server()

server.watch('template.html', on_reload)
server.serve(root='.')
