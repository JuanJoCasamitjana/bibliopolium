from bs4 import BeautifulSoup , Tag
import urllib.request 
from urllib.parse import urlencode
from .models import Book
import threading
from threading import Thread
from django.db import connections, transaction 
from queue import Queue
from datetime import datetime

global JOB_IS_ACTIVE
JOB_IS_ACTIVE = False

URL_TROA = "https://www.troa.es"
URL_TROA_BUSQ = URL_TROA+'/busqueda/listaLibros.php/'

URL_BOTICA = "https://www.libreriaboticadelectores.es" 
URL_BOTICA_BUSQ = URL_BOTICA + "/busqueda/listaLibros.php"

URL_PALAS = "https://www.libreriapalas.es"
SUB_URL_PALAS = {
    "Narrativa contemporanea":("/libros-de/narrativa-contemporanea-0101/","0101"),
    "Narrativa clasica":("/libros-de/narrativa-clasica-0102/","0102"),
    "Biografias, memorias":("/libros-de/biografias-memorias-03/","03"),
    "Clasicos grecolatinos":("/libros-de/clasicos-grecolatinos-04/","04"),
    "Infantil":("/libros-de/infantil-05/","05"),
    "Psicologia":("/libros-de/psicologia-0601/","0601"),
    "Educacion":("/libros-de/educacion-0603/","0603"),
    "Pintura, arquitectura":("/libros-de/pintura-arquitectura-0701/","0701"),
    "Cine, fotografia, musica, flamenco":("/libros-de/cine-fotografia-musica-flamenco-0702/","0702"),
    "Viajes":("/libros-de/viajes-08/","08"),
    "Turismo, mapas":("/libros-de/turismo-mapas-09/","09"),
    "Naturaleza, animales, plantas, senderismo":("/libros-de/naturaleza-animales-plantas-senderismo-10/","10"),
    "Caza, deporte, tauromaquia":("/libros-de/caza-deportes-tauromaquia-11/","11"),
    "Cocina, alimentacion, salud":("/libros-de/cocina-alimentacion-salud-12/","12"),
    "Historia de España":("/libros-de/historia-de-espana-1301/","1301"),
    "Historia universal":("/libros-de/historia-universal-1302/","1302"),
    "Geografia":("/libros-de/geografia-1402/","1402"),
    "Filosofia":("/libros-de/filosofia-1403/","1403"),
    "Sociologia":("/libros-de/sociologia-1404/","1404"),
    "Ciencia, divulgacion cientifica":("/libros-de/ciencia-divulgacion-cientifica-15/","15"),
    "Religiones, espiritualidad, mitologia":("/libros-de/religiones-espiritualidad-mitologia-16/","16"),
    "Economia":("/libros-de/economia-1701/","1701"),
    "Linguistica, teoria literaria, historia de la literatura":("/libros-de/linguistica-teoria-literaria-historia-de-la-lterat-18/","18"),
    "Narrativa ingles":("/libros-de/narrativa-en-ingles-1901/","1901"),
    "Narrativa frances":("/libros-de/narrativa-en-frances-1902/","1902"),
    "Narrativa aleman":("/libros-de/narrativa-en-aleman-1903/","1903"),
    "Narrativa italiano":("/libros-de/narrativa-en-italiano-1904/","1904"),
    "Narrativa portugues":("/libros-de/narrativa-en-portugues-1905/","1905"),
    "Poesia":("/libros-de/poesia-20/","20"),
    "Teatro":("/libros-de/teatro-21/","21"),
    "Ajedrez, juegos":("/libros-de/ajedrez-juegos-22/","22"),
    "Manualidades, decoracion":("/libros-de/manualidades-labores-decoracion-23/","23"),
    "Atlas geograficos":("/libros-de/atlas-geograficos-2401/","2401"),
    "Atlas historicos":("/libros-de/atlas-historicos-2402/","2402"),
    "Juvenil":("/libros-de/juvenil-25/","25"),
    "Sevilla, Andalucia":("/libros-de/temas-sevillanos-y-andaluces-30/","30"),
    "Ilustrados, comics":("/libros-de/ilustrados-comics-31/","31"),
    "Manga":("/libros-de/manga-32/","32"),
    "Arte":("/libros-de/arte-70/","70")

}

def scrape_troa(pages, theme):
    res_dict = {}
    for page in range(1,pages+1):
        params = {
            "pagSel": page,
            "cuantos": 40,
            "orden": "prioridad,fecha_edicion desc",
            "grupoLotes": "RECOMENDADOS",
            "categoriaLotes": theme,
            "tipoBusqueda": 1
        }
        url = f"{URL_TROA_BUSQ}?{urlencode(params)}"
        response = urllib.request.urlopen(url)
        soup = BeautifulSoup(response, 'lxml')
        books = soup.find_all('article', class_='product-list-item')
        for book in books:
            title_raw = book.find('a', class_='product-item-title')
            title = title_raw.string.strip()
            url_book = title_raw['href']
            author = book.find('div', class_='book-author').a.string.strip()
            image = book.find('a', class_='product-list-item-img').img['src']
            image_real = URL_TROA + image
            price = book.find('span', class_='product-item-price').strong.string.strip()
            price = float(price.split(" ")[0].replace(',','.'))
            url_real = URL_TROA+url_book
            category = theme
            res_dict[url_real] = Book(title=title,author=author,price=price, url=url_real, image=image_real, source="Troa", categories=category)


    return [book for book in res_dict.values()]

def scrape_botica(pages, theme):
    res_dict = {}
    for page in range(1, pages+1):
        params = {
            'tipoArticulo': "L",
            'pagSel': page,
            'orden': '''prioridad%2C+fecha_edicion+desc''',
            'cuantos': 30,
            'codMateria': theme,
        }
        url = f"{URL_BOTICA_BUSQ}?{('&'.join([f'{key}={value}' for key, value in params.items()]))}"
        response = urllib.request.urlopen(url)
        soup = BeautifulSoup(response, 'lxml')
        books = soup.find_all('li', class_="item")
        for book in books:
            url_book = book.find('a', class_='productClick')['href']
            image = book.find('img', class_='foto')['src']
            title = book.find('dd', class_='title').string.strip()
            author = book.find('dd', class_='creator')
            if author.string:
                author = author.string.strip()
            else:
                author = "Unkown"
            price = book.find('p', class_='precio').strong.string.split(" ")[0].strip().replace(',','.')
            url_real = URL_BOTICA + url_book
            if ',' in author:
                author = author.split(",")
                author = f"{author[1].strip()} {author[0].strip()}"
            res_dict[url_real]=Book(title=title, author=author, price=float(price), url=url_real, image=image, source="Botica de lectores", categories=theme)
    return [book for book in res_dict.values()]


def scrape_palas(pages, theme):
    res_dict = {}
    sub_url_y_cod = SUB_URL_PALAS[theme]
    sub_url = sub_url_y_cod[0]
    cod = sub_url_y_cod[1]
    for page in range(1, pages+1):
        params = {
            'tipoArticulo': "L",
            'pagSel': page,
            'orden': '''prioridad%2C+fecha_edicion+desc''',
            'cuantos': 30,
            'codMateria': cod,
        }
        url = f"{URL_PALAS}{sub_url}?{('&'.join([f'{key}={value}' for key, value in params.items()]))}"
        response = urllib.request.urlopen(url)
        soup = BeautifulSoup(response, 'lxml')
        books = soup.find_all('li', class_="item")
        for book in books:
            url_book = book.find('dd', class_='title').a['href']
            image = book.find('img', class_='foto')['src']
            title = book.find('dd', class_='title').a.string.strip()
            author = book.find('dd', class_='creator')
            if author.string:
                author = author.string.strip()
            else:
                author = "Unkown"
            if ',' in author:
                author = author.split(",")
                author = f"{author[1].strip()} {author[0].strip()}"
            price = book.find('p', class_='precio').strong.string.split(" ")[0].strip().replace(',','.')
            url_real = URL_PALAS + url_book
            res_dict[url_real]=Book(title=title, author=author, price=float(price), url=url_real, image=image, source="Palas", categories=theme)
    return [book for book in res_dict.values()]


def update_troa(book:Book):
    url = book.url
    response = urllib.request.urlopen(url)
    soup = BeautifulSoup(response, 'lxml')
    info = soup.find('div', class_='product-info-row')
    isbn = info.find('span', itemprop='isbn').string
    materia_element = info.find('span', text='Materia:') 
    materia = book.categories
    if materia_element:
        materia = materia_element.find_next('a').string
    synopsis = soup.find('div', id='tab-description-content').text
    book.isbn=isbn
    book.categories=materia
    book.synopsis = synopsis
    book.last_updated = datetime.now()
    return book

def update_botica(book:Book):
    url = book.url
    response = urllib.request.urlopen(url)
    soup = BeautifulSoup(response, 'lxml')
    synopsis_raw = soup.find('p', class_='bodytext')
    synopsis = ""
    if synopsis_raw and synopsis_raw.text:
        synopsis = synopsis_raw.text
    isbn_element = soup.find('dt', text='ISBN:')
    isbn = None
    if isbn_element:
        isbn = isbn_element.find_next('dd').text.strip()
    materia_element = soup.find('dt', text='Materia')
    materia = book.categories
    if materia_element:
        materia = materia_element.find_next('dd').find('a').text.strip()
    authors = soup.find('p', id='autor')
    if authors:
        authors = authors.find_all('span', class_='nomesigas')
    else:
        authors = [book.author,]
    authors_str = ""
    for author in authors:
        if author and isinstance(author, Tag):
            author = author.string
            if ',' in author:
                author = author.split(",")
                author = f"{author[1]} {author[0]}"
            if authors_str == "":
                authors_str = author
            else:
                authors_str = f"{authors_str}, {author}"
    book.author = authors_str
    book.isbn= isbn
    book.synopsis = synopsis
    book.categories = materia
    book.last_updated = datetime.now()
    return book



def update_palas(book:Book):
    url = book.url
    response = urllib.request.urlopen(url)
    soup = BeautifulSoup(response, 'lxml')
    synopsis_raw = soup.find('p', class_='bodytext')
    synopsis = ""
    if synopsis_raw and synopsis_raw.text:
        synopsis = synopsis_raw.text
    isbn_element = soup.find('dt', text='ISBN:')
    isbn = None
    if isbn_element:
        isbn = isbn_element.find_next('dd').text.strip()
    materia_element = soup.find('dt', text='Materia')
    materia = book.categories
    if materia_element:
        materia = materia_element.find_next('dd').find('a').text.strip()
    authors = soup.find('p', id='autor')
    if authors:
        authors = authors.find_all('a')
    else:
        authors = [book.author,]
    authors_str = ""
    for author in authors:
        if author and author.string:
            author = author.string
            if ',' in author:
                author = author.split(",")
                author = f"{author[1]} {author[0]}"
            if authors_str == "":
                authors_str = author
            else:
                authors_str = f"{authors_str}, {author}"
    book.author = authors_str
    book.isbn= isbn
    book.synopsis = synopsis
    book.categories = materia
    book.last_updated = datetime.now()
    return book
    

def book_update(book: Book):
    if book.source == "Troa":
        return update_troa(book)
    if book.source == "Botica de lectores":
        return update_botica(book)
    if book.source == "Palas":
        return update_palas(book)
    return book

def update_books_thread(book_slice):
        for book in book_slice:
            updated_book = book_update(book)
            updated_book.save()
def update_all_books_background():
    global JOB_IS_ACTIVE
    if not JOB_IS_ACTIVE:
        JOB_IS_ACTIVE = True
        thread = Thread(target=update_all_books_background_aux)
        thread.start()
    return

def update_all_books_background_aux():
    global JOB_IS_ACTIVE
    books = Book.objects.all()
    num_threads= 3
    books_slice_size = len(books) // 3
    threads = []
    for i in range(num_threads):
        start = i * books_slice_size
        end = (i + 1) * books_slice_size if i < num_threads - 1 else None
        thread_books = books[start:end]
        thread = Thread(target=update_books_thread, args=(thread_books,))
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()
    print("job finished")
    JOB_IS_ACTIVE = False
    