import string
from bs4 import BeautifulSoup , Tag
import urllib.request 
from urllib.parse import urlencode
from .models import Book, Category, Review, Reviewer, Alike
import threading
from threading import Thread
from django.db import connections, transaction 
from queue import Queue
from django.utils import timezone
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote
import shelve

global JOB_IS_ACTIVE
JOB_IS_ACTIVE = False

stopwords = {
    'a', 'an', 'the', 'and', 'but', 'or', 'nor',
    'for', 'so', 'yet', 'I', 'you', 'he', 'she', 'it', 'we', 'they',
    'to', 'in', 'on', 'at', 'by', 'with', 'of', 'from', 'off', 'over', 'under', 'above', 'below',
    'me', 'you', 'him', 'her', 'us', 'them', 'this', 'that', 'these', 'those',
    'here', 'there', 'where', 'when', 'while', 'before', 'after',
    'because', 'since', 'although', 'though', 'if', 'unless', 'not', 'no', 'yes',
    'oh', 'wow', 'aha', 'ohh', 'uh', 'uhh', 'hmm', 'huh','about', 'above', 'after', 
    'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', "aren't", 'as', 'at', 
    'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 
    'by', "can't", 'cannot', 'could', "couldn't", 'did', "didn't", 'do', 'does', 
    "doesn't", 'doing', "don't", 'down', 'during', 'each', 'few', 'for', 'from', 'further', 
    'had', "hadn't", 'has', "hasn't", 'have', "haven't", 'having', 'he', 
    "he'd", "he'll", "he's", 'her', 'here', "here's", 'hers', 'herself', 
    'him', 'himself', 'his', 'how', "how's", 'i', "i'd", "i'll", "i'm", 
    "i've", 'if', 'in', 'into', 'is', "isn't", 'it', "it's", 'its', 'itself', 
    "let's", 'me', 'more', 'most', "mustn't", 'my', 'myself', 'no', 'nor', 'not', 
    'of', 'off', 'on', 'once', 'only', 'or', 'other', 'ought', 'our', 'ours', 
    'ourselves', 'out', 'over', 'own', 'same', "shan't", 'she', "she'd", 
    "she'll", "she's", 'should', "shouldn't", 'so', 'some', 'such', 'than', 
    'that', "that's", 'the', 'their', 'theirs', 'them', 'themselves', 
    'then', 'there', "there's", 'these', 'they', "they'd", "they'll", 
    "they're", "they've", 'this', 'those', 'through', 'to', 'too', 'under', 
    'until', 'up', 'very', 'was', "wasn't", 'we', "we'd", "we'll", "we're", 
    "we've", 'were', "weren't", 'what', "what's", 'when', "when's", 'where', 
    "where's", 'which', 'while', 'who', "who's", 'whom', 'why', "why's", 
    'with', "won't", 'would', "wouldn't", 'you', "you'd", "you'll", "you're", 
    "you've", 'your', 'yours', 'yourself', 'yourselves'
}


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
    with shelve.open('unchecked') as db:
        not_found_data = db.setdefault('not_found', set())
        if 'not_found' not in db:
            db['not_found'] = not_found_data
        elif 'not_found' in db and not not_found_data:
            not_found_data = set()
            db['not_found'] = not_found_data
        error_data = set()
        db['error'] = error_data
        
        for i in index_list:
            if i in not_found_data:
                continue
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
                    reviewer.last_updated = timezone.now()
                    reviewer.save()
                if not created and (reviewer.name != name or reviewer.bio != bio, reviewer.bookBrowseID != i):
                    reviewer.name = name
                    reviewer.bio = bio
                    reviewer.bookBrowseID = i
                    reviewer.last_updated = timezone.now()
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
                    elif score == 'nostar':
                        score_int = 0
                    book,_ = Book.objects.get_or_create(url=book_url)
                    book.title = book_title
                    book.bookBrowseID = int(book_bbid)
                    book.last_updated = timezone.now()
                    book.save()
                    review,_ = Review.objects.get_or_create(url=review_url)
                    review.book = book
                    review.reviewer = reviewer
                    review.score = score_int
                    review.last_updated=timezone.now()
                    review.save()        
            except HTTPError as e:
                if e.code == 404:  # Captura el error 404 específicamente
                    not_found_data.add(i)
                    print(f"La URL {i} no fue encontrada. Ignorando. No encontrados: {not_found_data}")
                    db['not_found'] = not_found_data
                    continue
                else:
                    error_data.add(i)
                    print(f"Error de URL en la URL {i}, fallos: {error_data}")
                    db['error'] = error_data
                    continue
            except URLError as e:
                error_data.add(i)
                print(f"Error de URL en la URL {i}, fallos: {error_data}")
                db['error'] = error_data
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
        book.last_updated = timezone.now()
        book.save()
        review_db = Review.objects.get(url=url)
        review_text = soup.find('div', id='bookbrowse_review')
        if review_text:
            review_text = review_text.find('p', class_='')
        else:
            review_final = ''
            review_db.text=review_final
            review_db.last_updated=timezone.now()
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
                review_complete_list = review_complete.find_all('p')

                for p in review_complete_list:
                    parrafo = p.text
                    if parrafo:
                        if 'class' in p.attrs and 'freshness' in p['class']:
                            continue
                        review_final = f'{review_final} \n{parrafo.strip()}'
                review_db.text=review_final
                review_db.last_updated=timezone.now()
                review_db.save()
                if len(review_final)==0:
                    review_complete_list = review_complete.find_all('div', class_=['blockquote','text'])
                    for p in review_complete:
                        parrafo = p.text
                        review_final = f'{review_final} \n{parrafo.strip()}'
                    review_db.text=review_final
                    review_db.last_updated=timezone.now()
                    review_db.save()
            else:
                review_final = review_text.text
                review_db.text=review_final
                review_db.last_updated=timezone.now()
                review_db.save()
        else:
            review_final = review_text.text
            review_db.text=review_final
            review_db.last_updated=timezone.now()
            review_db.save()
            return

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
        book.last_updated= timezone.now()
        book.save()
    except URLError as e:
        print(e.strerror)
        time.sleep(10)
        get_book_tags(book)


def get_as_keywords(text: str)->str:
    if not text:
        return ''
    translator = str.maketrans("", "", string.punctuation)
    cleaned_text = text.translate(translator).lower()
    words = set(cleaned_text.split())
    keywords = [word for word in words if word not in stopwords]
    keywords_str = ', '.join(keywords)
    return keywords_str