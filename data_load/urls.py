from django.contrib import admin
from django.urls import path
from .views import  home, load_troa, load_botica, stats, load_palas, ficha_libro, update_all_books, update

urlpatterns = [
    path('load-troa/', load_troa, name="load_troa"),
    path('load-botica/', load_botica, name="load_botica"),
    path('load-palas/', load_palas, name="load_palas"),
    path('ficha-libro/<int:id>', ficha_libro, name="ficha_libro"),
    path('actualiza-libro/<int:id>', update, name="update"),
    path('stats/', stats, name="stats"),
    path('update-all/', update_all_books, name="update_all_books"),
    path('', home, name="home")
]
