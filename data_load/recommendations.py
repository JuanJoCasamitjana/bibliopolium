# encoding:utf-8
from .models import Category, Book, Reviewer, Review, Alike
from collections import Counter
import shelve
from django.db.models import Count
from datetime import datetime

def load_similarities():
    shelf = shelve.open('dataRS.dat')
    book_categories = top_book_categories()
    #reviewer_books = top_reviewers_books(book_categories)
    reviewer_categories = reviewer_top_categories()
    #reviewer_book_scores = get_reviewer_book_scores()
    #shelf['similarities'] = compute_similarities(book_categories, reviewer_books)
    shelf['similarities'] = compute_similarities2(book_categories, reviewer_categories)
    shelf['top_categories'] = reviewer_categories
    shelf.close()

def recommend_books(reviewer: Reviewer):
    res = []
    reviews = Review.objects.filter(reviewer=reviewer)
    if reviews:
        shelf = shelve.open("dataRS.dat")
        # conjunto de libros que ya ha revisado el revisor, que no se consideran para recomendar
        reviewed_books = set(review.book.id for review in reviews)
        for book_id, score in shelf['similarities'][reviewer.id]:
            if book_id not in reviewed_books:
                book_title = Book.objects.get(pk=book_id)
                res.append([book_title, 100 * score])
        shelf.close()
    return res

def top_categories_reviewer(reviewer: Reviewer):
    shelf = shelve.open("dataRS.dat")
    res = set()
    if 'top_categories' in shelf:
        top_categories = shelf['top_categories']
        categories_ids = top_categories[reviewer.pk]
        for id_c in categories_ids:
            cat = Category.objects.get(pk=id_c)
            res.add(cat)
        shelf.close
    return res


def compute_similarities(book_categories, reviewer_books):
    # Calcula la matriz de similaridad entre revisores y libros (coeficiente de Dice). Solo los 20 más similares se almacenan
    res = {}
    for r in reviewer_books:
        top_books = {}
        for b in book_categories:
            top_books[b] = jaccard_coefficient(reviewer_books[r], book_categories[b])
        res[r] = Counter(top_books).most_common(20)
    return res

def top_book_categories():
    # Obtiene las categorías de cada libro sin considerar frecuencias
    categories = {}
    for book in Book.objects.all():
        book_id = book.id
        categories[book_id] = set(category.id for category in book.categories.all())
    return categories


def top_reviewers_books(book_categories):
    # Calcula el conjunto de libros de los diez revisores más activos
    reviewers = {}
    previous = -1
    total = 1
    for e in Reviewer.objects.values('id', 'review__book__id').order_by('id'):
        if e['id'] == previous and total <= 10:
            if e['review__book__id'] in book_categories.keys():
                reviewers[e['id']].union(book_categories[e['review__book__id']])
                total += 1
        else:
            if e['review__book__id'] in book_categories.keys():
                reviewers[e['id']] = set(book_categories[e['review__book__id']])
                total = 1
                previous = e['id']
    return reviewers

def jaccard_coefficient(set1, set2):
    return len(set1.intersection(set2)) / len(set1.union(set2))

def get_reviewer_book_scores():
    reviews = Review.objects.select_related('book', 'reviewer').all()
    # reviewer_book_score['reviewer_id']['book_id'] = score
    reviewer_book_score = dict()
    for review in reviews:
        reviewer_id = review.reviewer.id
        book_id = review.book.id
        score = review.score
        if reviewer_id not in reviewer_book_score:
            reviewer_book_score[reviewer_id] = {}
        reviewer_book_score[reviewer_id][book_id] = score
    return reviewer_book_score


def reviewer_top_categories():
    reviews = Review.objects.select_related('book', 'reviewer').all()
    top_categories_by_reviewer = dict()
    for review in reviews:
        reviewerId = review.reviewer.pk
        if reviewerId not in top_categories_by_reviewer:
            top_categories_by_reviewer[reviewerId] = Counter()
        categories = review.book.categories.all()
        for category in categories:
            top_categories_by_reviewer[reviewerId][category.pk] += 1
    top_categories_dict = dict()
    for reviewerId, category_counter in top_categories_by_reviewer.items():
        top_categories_dict[reviewerId] = set(category_id for category_id, _ in category_counter.most_common(5))
    return top_categories_dict

def compute_similarities2(book_categories, reviewer_categories):
    res = {}
    for r in reviewer_categories:
        top_books = {}
        for b in book_categories:
            top_books[b] = jaccard_coefficient(reviewer_categories[r], book_categories[b])
        res[r] = Counter(top_books).most_common(20)
    return res