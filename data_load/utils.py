from bs4 import BeautifulSoup
import urllib.request 
from urllib.parse import urlencode
from .models import Book

URL_TROA = "https://www.troa.es"
URL_TROA_BUSQ = URL_TROA+'/busqueda/listaLibros.php/'

URL_BOTICA = "https://www.libreriaboticadelectores.es" 
URL_BOTICA_BUSQ = URL_BOTICA + "/busqueda/listaLibros.php"

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

    params = {
        'tipoArticulo': "L",
        'pagSel': 1,
        'orden': '''prioridad%2C+fecha_edicion+desc''',
        'cuantos': pages*30,
        'codMateria': theme,
    }
    url = f"{URL_BOTICA_BUSQ}?{('&'.join([f'{key}={value}' for key, value in params.items()]))}"
    print(url)
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