from django.contrib import admin
from django.urls import path
from .views import  home, stats, ficha_libro, load_tags, list_tags, load_books_of_tag, delete_all_books, load_reviewers, list_reviews
from .views import  load_full_reviews, review_details, reviewer_details, list_reviewers, load_book_tags, list_books_without_categories
from .views import list_by_category, load_menu, update_review_and_book, load_whoosh_index, instructions, load_recommendation
from .views import recommend_book, login_admin, logout_admin
urlpatterns = [
    path('ficha-libro/<int:id>', ficha_libro, name="ficha_libro"),
    path('stats/', stats, name="stats"),
    path('list-tags/', list_tags, name="list_tags"),
    path('load-tags/', load_tags, name="load_tags"),
    path('load-books-of-tag/', load_books_of_tag, name="load_books_of_tag"),
    path('delete-all-books/', delete_all_books, name="delete_all_books"),
    path('load-reviewers/', load_reviewers, name="load_reviewers"),
    path('list-reviews/', list_reviews, name="list_reviews"),
    path('load-reviews/', load_full_reviews, name="load_full_reviews"),
    path('review/<int:id>', review_details, name="review_details"),
    path('reviewer/<int:id>', reviewer_details, name="reviewer_details"),
    path('list-reviewers/', list_reviewers, name="list_reviewers"),
    path('load-book-tags/', load_book_tags, name="load_book_tags"),
    path('list-books-no-categories/', list_books_without_categories, name="list_books_without_categories"),
    path('list-books-by-category/<int:id>', list_by_category, name="list_by_category"),
    path('load-operations/', load_menu, name="load_menu"),
    path('review-update/<int:id>', update_review_and_book, name="update_review_and_book"),
    path('load-whoosh/', load_whoosh_index, name="load_whoosh_index"),
    path('instructions/', instructions, name="instructions"),
    path('load-recommendation/', load_recommendation, name="load_recommendation"),
    path('reviewer-recommend/<int:id>', recommend_book, name="recommend_book"),
    path('log-in/', login_admin, name="login_admin"),
    path('log-out/', logout_admin, name="logout_admin"),
    path('', home, name="home")
]
