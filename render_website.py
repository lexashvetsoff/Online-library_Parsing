from livereload import Server
from jinja2 import Environment, FileSystemLoader, select_autoescape
from more_itertools import chunked
from urllib.parse import quote
import json
import math
import os

with open('books_data.json', 'r', encoding="utf8") as file:
    books_data = json.load(file)

if os.sep == '\\':
    for book in books_data:
        book['img_src'] = book['img_src'].replace('\\', '/')
        book['book_path'] = book['book_path'].replace('\\', '/')
        book['book_path'] = quote(book['book_path'])


def on_reload():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')

    d_books = list(chunked(books_data, 20))
    
    for page_number, books in enumerate(d_books, 1):
        file_name = f'index{page_number}.html'
        folder = 'pages'

        all_pages = math.ceil(len(books_data) / 20)
        
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


on_reload()

server = Server()

server.watch('template.html', on_reload)
server.serve(root='.')
