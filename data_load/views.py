from django.shortcuts import render
from .utils import  scrape_troa, scrape_botica
from .models import Book
from django.db.models import Count
from .forms import PagesForm, TroaForm, BoticaForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# Create your views here.



def load_troa(request):
    if request.method == 'POST':
        form = TroaForm(request.POST)
        if form.is_valid():
            pages = form.cleaned_data['pages']
            theme = form.cleaned_data['theme']
            books = scrape_troa(pages, theme)
            to_save = [] 
            for book in books:
                res = Book.objects.filter(url=book.url)
                if not res.exists():
                    to_save.append(book)
            books_db=Book.objects.bulk_create(to_save)
            return render(request, 'vista_libros.html', {'books':books_db})

    else:
        form = TroaForm()
        return render(request, 'form.html', {'form':form})

def home(request):
    books_list = Book.objects.all()

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

def load_botica(request):
    if request.method == 'POST':
        form = BoticaForm(request.POST)
        if form.is_valid():
            pages = form.cleaned_data['pages']
            theme = form.cleaned_data['theme']
            books = scrape_botica(pages, theme)
            to_save = [] 
            for book in books:
                res = Book.objects.filter(url=book.url)
                if not res.exists():
                    to_save.append(book)
            books_db=Book.objects.bulk_create(to_save)
            return render(request, 'vista_libros.html', {'books':books_db})

    else:
        form = BoticaForm()
        return render(request, 'form.html', {'form':form})


def stats(request):
    total_books = Book.objects.count()
    books_by_source = Book.objects.values('source').annotate(num_libros=Count('id'))
    bbs_dict = {item['source']: item['num_libros'] for item in books_by_source}
    return render(request, 'stats.html', {'total':total_books, 'by_source':bbs_dict})