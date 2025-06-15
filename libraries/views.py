from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Library
from .forms import LibraryForm

@login_required
def library_list(request):
    libraries = Library.objects.all()
    context = {
        'active_menu': 'libraries',
        'libraries': libraries
    }
    return render(request, 'libraries/library_list.html', context)

@login_required
def library_detail(request, library_id):
    library = get_object_or_404(Library, id=library_id)
    available_books = library.books.filter(status='available').count()
    
    context = {
        'active_menu': 'libraries',
        'library': library,
        'available_books': available_books
    }
    return render(request, 'libraries/library_detail.html', context)

@login_required
def library_create(request):
    if request.method == 'POST':
        form = LibraryForm(request.POST)
        if form.is_valid():
            library = form.save(commit=False)
            library.owner = request.user
            library.save()
            form.save_m2m()  # Save many-to-many relationships (admins)
            messages.success(request, f"Kütüphane '{library.name}' başarıyla oluşturuldu.")
            return redirect('libraries:detail', library_id=library.id)
    else:
        form = LibraryForm()
    
    context = {
        'active_menu': 'libraries',
        'form': form
    }
    return render(request, 'libraries/library_form.html', context)

@login_required
def library_edit(request, library_id):
    library = get_object_or_404(Library, id=library_id)
    
    if request.method == 'POST':
        form = LibraryForm(request.POST, instance=library)
        if form.is_valid():
            form.save()
            messages.success(request, f"Kütüphane '{library.name}' başarıyla güncellendi.")
            return redirect('libraries:detail', library_id=library.id)
    else:
        form = LibraryForm(instance=library)
    
    context = {
        'active_menu': 'libraries',
        'form': form,
        'library': library
    }
    return render(request, 'libraries/library_form.html', context)

@login_required
def library_delete(request, library_id):
    # Library delete logic here
    return redirect('libraries:list')
