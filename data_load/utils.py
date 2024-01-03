from bs4 import BeautifulSoup , Tag
import urllib.request 
from urllib.parse import urlencode
from .models import Book, Category, Review, Reviewer, Alike
import threading
from threading import Thread
from django.db import connections, transaction 
from queue import Queue
from datetime import datetime
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote

global JOB_IS_ACTIVE
JOB_IS_ACTIVE = False

TAG_URL = 'https://www.bookbrowse.com/category/index.cfm/tc/tags'
BASE_URL = 'https://www.bookbrowse.com'
REVIEWERS = 'https://www.bookbrowse.com/reviewers/index.cfm/fuseaction/details/reviewer_number/'
def get_tags():
    response = urllib.request.urlopen(TAG_URL)
    soup = BeautifulSoup(response, 'lxml')
    tabs = soup.find('div', class_='newtabs').find_all('div', class_='tab_content')
    tag_list = []
    for tab in tabs:
        
        links = tab.find_all('a')
        for link in links:
            url = link['href']
            name = link.text.strip()
            category = Category(url=url, name=name)
            tag_list.append(category)
    return tag_list

def get_books_of_tag(tag_url):
    response = urllib.request.urlopen(tag_url)
    soup = BeautifulSoup(response, 'lxml')
    pages_total = soup.find('p', class_='newcenter')
    total = pages_total.text.split(' ')[-1]
    max_page = int(total)
    books_list = soup.find('div', class_='display_block nav').find('div', class_='display_jackets clear').find('ul').find_all('li')
    books_dict={}
    for book in books_list:
        book_obj = Book()
        url = book.a['href']
        title = book.a.img['alt']
        image_base = book.a.img['src']
        image_url = f"{BASE_URL}{image_base}"
        book_obj.title=title
        book_obj.url=url
        book_obj.image=image_url
        books_dict[url] = book_obj

    next_page = 2
    while next_page<=max_page:
        next_page_url = soup.find('div', class_='pager clear').find('a', string=next_page.__str__())['href']
        response = urllib.request.urlopen(next_page_url)
        soup = BeautifulSoup(response, 'lxml')
        books_list = soup.find('div', class_='display_block nav').find('div', class_='display_jackets clear').find('ul').find_all('li')
        for book in books_list:
            book_obj = Book()
            url = book.a['href']
            title = book.a.img['alt']
            image_base = book.a.img['src']
            image_url = f"{BASE_URL}{image_base}"
            book_obj.title=title
            book_obj.url=url
            book_obj.image=image_url
            books_dict[url] = book_obj
        next_page = next_page + 1
        time.sleep(2)
    return [book for book in books_dict.values()]

def get_reviewers(index_list):
    unchecked = []
    for i in index_list:
        url = f"{REVIEWERS}{i}"
        try:
            response = urllib.request.urlopen(url)
            soup = BeautifulSoup(response, 'lxml')
            if soup.find('h1', string='Reviewer not found'):
                continue
            reviewer_file = soup.find('div', class_='clear')
            name = reviewer_file.find('h2').string.strip()
            bio = reviewer_file.find('div', class_='desc')
            if bio:
                bio = bio.text
            else:
                bio = ""
            reviews = soup.find('div', class_='display_block').find_all('div', class_='left_70')
            reviewer,created = Reviewer.objects.get_or_create(url=url)
            if created:
                reviewer.name = name
                reviewer.bio = bio
                reviewer.bookBrowseID = i
                reviewer.last_updated = datetime.now()
                reviewer.save()
            if not created and (reviewer.name != name or reviewer.bio != bio, reviewer.bookBrowseID != i):
                reviewer.name = name
                reviewer.bio = bio
                reviewer.bookBrowseID = i
                reviewer.last_updated = datetime.now()
                reviewer.save()
            print(reviewer)
            for review in reviews:
                book_title = review.a.b.string
                review_url = review.a['href']
                book_url = review_url.split('#')[0]
                book_bbid = book_url.split('/')[-1]
                score = review.find_next('div', class_='right_30').div['id']
                score_int = -1
                if score == 'fivestar':
                    score_int = 5
                elif score == 'fourstar':
                    score_int = 4
                elif score == 'threestar':
                    score_int = 3
                elif score == 'twostar':
                    score_int = 2
                elif score == 'onestar':
                    score_int = 1
                book,_ = Book.objects.get_or_create(url=book_url)
                book.title = book_title
                book.bookBrowseID = int(book_bbid)
                book.last_updated = datetime.now()
                book.save()
                review,_ = Review.objects.get_or_create(url=review_url)
                review.book = book
                review.reviewer = reviewer
                review.score = score_int
                review.last_updated=datetime.now()
                review.save()        
        except HTTPError as e:
            if e.code == 404:  # Captura el error 404 específicamente
                print(f"La URL {i} no fue encontrada. Ignorando.")
                continue
            else:
                print(f"La URL {i} tuvo un error. Ignorando.")
                unchecked.append(i)
                continue
        except URLError as e:
            print(f"Error de URL en la URL {i}: {e.reason} Ignorando.")
            unchecked.append(i)
            continue
        
def get_review(url):
    try:
        url = quote(url, safe=':/#')
        response = urllib.request.urlopen(url)
        soup = BeautifulSoup(response, 'lxml')
        book_url = url.split('#')[0]
        book_bbid = book_url.split('/')[-1]
        author = soup.find('div', class_='desc').find('p', class_='').a.string.strip()
        image = soup.find('img', class_='jacket')['src']
        summary_raw = soup.find('div', id='summary').find_all('p')
        summary = ''
        for p in summary_raw:
            parrafo = p.text
            if parrafo:
                summary = f'{summary} \n{parrafo.strip()}'
        book = Book.objects.get(bookBrowseID=book_bbid)
        book.author = author
        book.image = BASE_URL+image
        book.synopsis=summary
        response_book = urllib.request.urlopen(book.url)
        soup_book = BeautifulSoup(response_book, 'lxml')
        alike_db,_ = Alike.objects.get_or_create(book=book)
        alikes = soup_book.find('div', class_='readalikes_content clear').find_all('li')
        for alike in alikes:
            bbid = alike.figure.a['href'].split('/')[-2]
            similar_book = Book.objects.filter(bookBrowseID=bbid).first()
            if similar_book:
                alike_db.similarities.add(similar_book)
        alike_db.save()
        tags = soup_book.find('div', id='genres_themes').find_all('li')
        for tag in tags:
            name = tag.a.text.strip()
            category = Category.objects.filter(name=name).first()
            if category:
                book.categories.add(category)
        book.last_updated = datetime.now()
        book.save()
        review_db = Review.objects.get(url=url)
        review_text = soup.find('div', id='bookbrowse_review')
        if review_text:
            review_text = review_text.find('p', class_='')
        else:
            review_final = ''
            review_db.text=review_final
            review_db.last_updated=datetime.now()
            review_db.save()
            return
        link_review = review_text.find('a', href=lambda href: href and '#' in href)
        if link_review:
            review_link = link_review['href']
            review_link = quote(review_link, safe=':/#')
            response_review = urllib.request.urlopen(review_link)
            soup_review = BeautifulSoup(response_review, 'lxml')
            review_complete = soup_review.find('div', id='review')
            review_final = ''
            if review_complete:
                review_complete = review_complete.find_all('p')
            
                for p in review_complete:
                    parrafo = p.text
                    if parrafo:
                        if 'class' in p.attrs and 'freshness' in p['class']:
                            continue
                        review_final = f'{review_final} \n{parrafo.strip()}'
                review_db.text=review_final
                review_db.last_updated=datetime.now()
                review_db.save()
            else:
                review_final = review_text.text
                review_db.text=review_final
                review_db.last_updated=datetime.now()
                review_db.save()

    except URLError as e:
        print(e.strerror)
        time.sleep(10)
        get_review(url)


def get_book_tags(book: Book):
    try:
        alike_db,_ = Alike.objects.get_or_create(book=book)
        response = urllib.request.urlopen(book.url)
        soup = BeautifulSoup(response, 'lxml')
        alikes = soup.find('div', class_='readalikes_content clear').find_all('li')
        for alike in alikes:
            bbid = alike.figure.a['href'].split('/')[-2]
            similar_book = Book.objects.filter(bookBrowseID=bbid).first()
            if similar_book:
                alike_db.similarities.add(similar_book)
        alike_db.save()
        tags = soup.find('div', id='genres_themes').find_all('li')
        for tag in tags:
            name = tag.a.text.strip()
            category = Category.objects.filter(name=name).first()
            if category:
                book.categories.add(category)
        book.last_updated= datetime.now()
        book.save()
    except URLError as e:
        print(e.strerror)
        time.sleep(10)
        get_book_tags(book)