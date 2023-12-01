from django.contrib import admin
from django.urls import path
from .views import  home, load_troa, load_botica, stats

urlpatterns = [
    path('load-troa/', load_troa, name="load_troa"),
    path('load-botica/', load_botica, name="load_botica"),
    path('stats/', stats, name="stats"),
    path('', home, name="home")
]
