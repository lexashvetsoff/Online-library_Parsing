import requests
import os


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


directory_name = 'books'
if not os.path.exists(directory_name):
    os.makedirs(directory_name, exist_ok=True)

url = 'https://tululu.org/txt.php'

for i in range(1, 11):
    payload = {"id": i}

    response = requests.get(url, params=payload)
    response.raise_for_status()

    try:
        check_for_redirect(response)
        filename = f'books/id{i}.txt'
        with open(filename, 'wb') as file:
            file.write(response.content)
    except requests.HTTPError:
        print('Такой книги нет!')