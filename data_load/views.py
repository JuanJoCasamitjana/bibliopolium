from django.shortcuts import render, redirect
from .utils import  scrape_troa, scrape_botica, scrape_palas, book_update, update_all_books_background
from .models import Book
from django.db.models import Count
from .forms import PagesForm, TroaForm, BoticaForm, PalasForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# Create your views here.




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
    total_books = Book.objects.count()
    books_by_source = Book.objects.values('source').annotate(num_libros=Count('id'))
    bbs_dict = {item['source']: item['num_libros'] for item in books_by_source}
    return render(request, 'stats.html', {'total':total_books, 'by_source':bbs_dict})

def load(request, scrape_function, form):
    if request.method == 'POST':
        form = form(request.POST)
        if form.is_valid():
            pages = form.cleaned_data['pages']
            theme = form.cleaned_data['theme']
            books = scrape_function(pages, theme)
            to_save = [] 
            for book in books:
                res = Book.objects.filter(url=book.url)
                if not res.exists():
                    to_save.append(book)
            books_db=Book.objects.bulk_create(to_save)
            return render(request, 'vista_libros.html', {'books':books_db})

    else:
        form = form()
        return render(request, 'form.html', {'form':form})

def load_palas(request):
    return load(request, scrape_palas ,PalasForm)

def load_botica(request):
    return load(request, scrape_botica ,BoticaForm)
    
def load_troa(request):
    return load(request, scrape_troa ,TroaForm)

def ficha_libro(request, id):
    book = Book.objects.get(id=id)
    return render(request, 'ficha_libro.html', {'book':book})

def update(request, id):
    book = Book.objects.get(id=id)
    book = book_update(book)
    book.save()
    return render(request, 'ficha_libro.html', {'book':book})

def update_all_books(request):
    update_all_books_background()
    return redirect('home')
