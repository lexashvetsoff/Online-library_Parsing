# Парсер книг с сайта tululu.org

Скрипт скачивает книги с сайта tululu.org и создает веб-сайт с ними.

### Где посмотреть

Пример сайта можно увидеть посмотреть здесь - [онлайн библиотека](https://lexashvetsoff.github.io/Online-library_Parsing/pages/index1.html).

### Как установить

Для запуска блога у вас уже должен быть установлен Python 3.
Установите зависимости командой `pip install -r requirements.txt`

### Аргументы

#### parse_tululu_category.py
Скрипт скачивает книги с [tululu.org](tululu.org) и собирает информацию по ним.  

У скрипта есть параметры:  
     `--start_page` - по умолчанию = 1 - начальная страница скачивания  
     `--end_page` - по умолчанию = номеру последней страницы - конечная страница скачивания  
     `--dest_folder_img` - по умолчанию = images/ - название папки для хранения скачаных картинок  
     `--dest_folder_txt` - по умолчанию = books/ - название папки для хранения скачаных книг  
     `--skip_imgs` - по умолчанию = False - пропускать ли скачивание картинок  
     `--skip_txt` - по умолчанию = False - пропускать ли скачивание книг  
     `--json_path` - по умолчанию = data_books.json - путь к файлу json в котором хранятся данные по книгам  
Передаются параметры при запуске скрипта в командной строке:
```
python parse_tululu_category.py --start_page=10 --end_page=11
```
Скачаются книги со страниц 10 и 11, картинки будут хранится в папке images, книги - books, корне каталога создастся файл data_books.json с данными по скачанным книгам.

Если запустить скрипт не передавая эти параметры:
```
python parse_tululu_category.py
```
Скачаются книги со всех страниц, картинки будут хранится в папке images, книги - books, корне каталога создастся файл data_books.json с данными по скачанным книгам.

#### render_website.py
Формирует веб сайт из данных полученных скриптом `parse_tululu_category.py`.  
Для запуска введите команду:  
```
python render_website.py
```

### Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).