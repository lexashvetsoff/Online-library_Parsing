from livereload import Server
from jinja2 import Environment, FileSystemLoader, select_autoescape
from more_itertools import chunked
import json
import os

with open('data_books.json', 'r', encoding="utf8") as file:
    data_books_json = file.read()
data_books = json.loads(data_books_json)

if os.sep == '\\':
    for book in data_books:
        book['img_src'] = book['img_src'].replace('\\', '/')
        book['book_path'] = book['book_path'].replace('\\', '/')


def on_reload():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')

    if len(data_books) % 2 != 0:
        books = list(chunked(data_books, len(data_books) - 1))
        rendered_page = template.render(
            books = books[0]
        )
    else:
        rendered_page = template.render(
            books = data_books
        )

    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)

on_reload()

server = Server()

server.watch('template.html', on_reload)
server.serve(root='.')
