import os
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from .models import Book, Category, Reviewer, Review, Alike
from django.db.models import Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .utils import get_tags, get_books_of_tag, get_reviewers, get_review, get_book_tags, get_as_keywords
from .forms import LoadOfTagForm, LoadReviewersForm, LoadReviewsForm, LoadBookTagsForm
from threading import Thread
from whoosh.index import create_in
from whoosh.fields import TEXT, ID, Schema, DATETIME, KEYWORD, NUMERIC
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh.qparser.dateparse import DateParserPlugin
from whoosh.query import Term
from whoosh import qparser
from whoosh.index import open_dir
from .recommendations import load_similarities, recommend_books, top_categories_reviewer
import shelve
# Create your views here.

directory='./schema_index'
sch = Schema(
    bookId=NUMERIC(stored=True,numtype=int),
    reviewId=NUMERIC(stored=True,numtype=int),
    reviewerId=NUMERIC(stored=True,numtype=int),
    title=TEXT(),
    author=TEXT(),
    synopsis=KEYWORD(stored=True, commas=True),
    reviewText=KEYWORD(stored=True, commas=True),
    score=NUMERIC(stored=True,numtype=float)
    )


def home(request):
    books_list = Book.objects.all().order_by('id')

    # Configura el paginador
    paginator = Paginator(books_list, 40)  # Muestra 10 libros por página

    # Obtiene el número de página desde la solicitud GET
    page = request.GET.get('page')

    try:
        # Obtiene la lista de libros para la página solicitada
        books = paginator.page(page)
    except PageNotAnInteger:
        # Si la página no es un número entero, entrega la primera página
        books = paginator.page(1)
    except EmptyPage:
        # Si la página está fuera de rango (por encima de la última), entrega la última página
        books = paginator.page(paginator.num_pages)

    return render(request, 'vista_libros.html', {'books': books})



def stats(request):
    total = dict()
    total['Books'] = Book.objects.count()
    total['Reviews'] = Review.objects.count()
    total['Reviewers'] = Reviewer.objects.count()
    return render(request, 'stats.html', {'total':total})


def ficha_libro(request, id):
    book = Book.objects.get(id=id)
    alike = Alike.objects.filter(book=book).first()
    
    return render(request, 'ficha_libro.html', {'book':book, 'alike':alike})

def load_tags(request):
    tag_list = get_tags()
    all_tags_url = Category.objects.values_list('url', flat=True)
    tags_to_save = [tag for tag in tag_list if tag.url not in all_tags_url]
    tags_to_update = [tag for tag in tag_list if tag.url in all_tags_url]
    saved_tags = Category.objects.bulk_create(tags_to_save)
    all_tags = Category.objects.all()
    tags_and_info = []
    for tag in all_tags:
        tag_and_book_count = {
            'tag':tag,
            'book_count':len(tag.book_set.all())
        }
        tags_and_info.append(tag_and_book_count)
    count = len(all_tags)
    return render(request, 'tag_list.html', {'tags':tags_and_info, 'count':count})

def list_tags(request):
    all_tags = Category.objects.all()
    tags_and_info = []
    for tag in all_tags:
        tag_and_book_count = {
            'tag':tag,
            'book_count':len(tag.book_set.all())
        }
        tags_and_info.append(tag_and_book_count)
    count = len(all_tags)
    count_all_books = Book.objects.count()
    return render(request, 'tag_list.html', {
        'tags':tags_and_info, 
        'count':count,
        'book_count':count_all_books,
        })

def load_books_of_tag(request):
    if request.method == 'POST':
        form = LoadOfTagForm(request.POST)
        if form.is_valid():
            tag = form.cleaned_data['tag']
            url_tag = tag.url
            books=get_books_of_tag(url_tag)
            for book in books:
                book_db, created = Book.objects.get_or_create(url=book.url)
                book_db.title = book.title
                book_db.image = book.image
                book_db.categories.add(tag)
                book_db.save()
            return redirect('home')
    else:
        form = LoadOfTagForm()
        return render(request, 'form.html', {'form':form})

def delete_all_books(request):
    Book.objects.all().delete()
    return redirect('home')

def load_reviewers(request):
    if request.method == 'POST':
        form = LoadReviewersForm(request.POST)
        if form.is_valid():
            option = form.cleaned_data['choice']
            if option == 'All':
                indexes = range(2,170)
                ''' thread = Thread(target=get_reviewers,args=(indexes,))
                thread.start() '''
                get_reviewers(indexes)
            if option == 'Unchecked':
                with shelve.open('unchecked') as db:
                    print(db['error'])
                    print(db['not_found'])
                    error_data = db.get('error', set())
                    if 'error' not in db:
                        db['error'] = error_data
                    elif 'error' in db and not error_data:
                        error_data = set()
                        db['error'] = error_data
                    print(error_data)
                    get_reviewers(error_data)
                ''' thread = Thread(target=get_reviewers,args=(unchecked,))
                thread.start() '''
            return redirect('home')
    else:
        form = LoadReviewersForm()
        return render(request, 'form.html', {'form':form})
    
def list_reviews(request):
    reviews_list = Review.objects.all().order_by('id')

    # Configura el paginador
    paginator = Paginator(reviews_list, 60)  # Muestra 10 libros por página

    # Obtiene el número de página desde la solicitud GET
    page = request.GET.get('page')

    try:
        # Obtiene la lista de libros para la página solicitada
        reviews = paginator.page(page)
    except PageNotAnInteger:
        # Si la página no es un número entero, entrega la primera página
        reviews = paginator.page(1)
    except EmptyPage:
        # Si la página está fuera de rango (por encima de la última), entrega la última página
        reviews = paginator.page(paginator.num_pages)

    return render(request, 'review_list.html', {'reviews': reviews})

def load_full_reviews(request):
    if request.method == 'POST':
        form = LoadReviewsForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            objs = len(Review.objects.all())
            reviews_url =  Review.objects.all().order_by('last_updated')[:min(amount, objs)].values_list('url', flat=True)
            for url in reviews_url:
                get_review(url)
            return redirect('list_reviews')
    else:
        form = LoadReviewsForm()
        return render(request, 'form.html', {'form':form})
    

def review_details(request, id):
    review = get_object_or_404(Review, pk=id)
    return render(request, 'review_details.html', {'review': review})

def reviewer_details(request, id):
    reviewer = get_object_or_404(Reviewer, pk=id)
    reviews_list = get_list_or_404(Review, reviewer= reviewer)
    reviews = dict()
    reviews['total'] = len(reviews_list)
    reviews['list'] = reviews_list
    top_categories = top_categories_reviewer(reviewer)
    return render(request, 'reviewer_details.html', {'reviewer': reviewer, 'reviews':reviews, 'top_categories':top_categories})

def list_reviewers(request):
    reviewers_list = Reviewer.objects.all()
    reviewers = []
    for reviewer in reviewers_list:
        details = dict()
        details['reviewer'] = reviewer
        details['reviews'] = Review.objects.filter(reviewer=reviewer).count()
        reviewers.append(details)
    return render(request, 'reviewer_list.html', {'reviewers':reviewers})

def load_book_tags(request):
    if request.method == 'POST':
        form = LoadBookTagsForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            all_count = len(Review.objects.all())
            books = Book.objects.all().order_by('last_updated')[:min(amount, all_count)]
            for book in books:
                get_book_tags(book)
        return redirect('home')
    else:
        form = LoadBookTagsForm()
        return render(request, 'form.html', {'form':form})
    
def list_books_without_categories(request):
    books = Book.objects.annotate(num_categories=Count('categories')).filter(num_categories=0)
    return render(request, 'books_no_categories.html', {'books':books})

def list_by_category(request, id):
    category = get_object_or_404(Category, pk=id)
    books = category.book_set.all()
    return render(request, 'books_of_category.html', {'books':books, 'category': category})

def load_menu(request):
    return render(request,'load_menu.html')

def update_review_and_book(request, id):
    review = get_object_or_404(Review, pk=id)
    get_review(review.url)
    return redirect('review_details', id=id)

def load_whoosh_index(request):
    if not os.path.exists(directory):
        os.mkdir(directory)
    whoosh_index = create_in(directory, sch)
    reviews = Review.objects.all()
    k=0
    objs = len(reviews)
    for review in reviews:
        writer = whoosh_index.writer()
        writer.add_document(
            bookId=review.book.pk,
            reviewId=review.pk,
            reviewerId=review.reviewer.pk,
            title=review.book.title,
            author=review.book.author,
            synopsis=get_as_keywords(review.book.synopsis),
            reviewText=get_as_keywords(review.text),
            score=float(review.score)
        )
        writer.commit()
        k=k+1
        print(f"{k} de {objs} procesados: Review {review.pk} by {review.reviewer.name}")
    with whoosh_index.searcher() as searcher:
        query = qparser.QueryParser("reviewId", sch).parse('*')
        results = list(searcher.search(query, limit=None))
        num_entries = len(results)
    return render(request, 'whoosh_load.html', {'num_entries':num_entries})


def instructions(request):
    return render(request, 'instructions.html')

def load_recommendation(request):
    load_similarities()
    return redirect('home')

def recommend_book(request, id):
    reviewer = Reviewer.objects.get(pk=id)
    books = recommend_books(reviewer)
    return render(request, 'recommended_books.html', {'books':books, 'reviewer': reviewer})
