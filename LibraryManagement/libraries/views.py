from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from .models import Library
from .forms import LibraryForm
from books.models import Book

@login_required
def library_list(request):
    # Kullanıcı tipine göre kütüphaneleri filtrele
    if request.user.is_super_admin():
        # Süper admin tüm kütüphaneleri görebilir
        libraries = Library.objects.all()
    else:
        # Diğer kullanıcılar sadece kendi kütüphanelerini görebilir
        libraries = Library.objects.filter(owner=request.user)
    
    return render(request, 'libraries/library_list.html', {'libraries': libraries})

@login_required
def library_detail(request, pk):
    library = get_object_or_404(Library, pk=pk)
    
    # Erişim kontrolü
    if not (request.user.is_super_admin() or library.owner == request.user):
        return HttpResponseForbidden("Bu kütüphaneyi görüntüleme izniniz yok.")
    
    # Kütüphanedeki kitapları getir
    books = Book.objects.filter(library=library)
    
    context = {
        'library': library,
        'books': books
    }
    
    return render(request, 'libraries/library_detail.html', context)

@login_required
def create_library(request):
    if request.method == 'POST':
        form = LibraryForm(request.POST)
        if form.is_valid():
            library = form.save(commit=False)
            library.owner = request.user
            library.save()
            messages.success(request, 'Kütüphane başarıyla oluşturuldu!')
            return redirect('library_detail', pk=library.pk)
    else:
        form = LibraryForm()
    
    return render(request, 'libraries/library_form.html', {'form': form, 'title': 'Yeni Kütüphane Oluştur'})

@login_required
def edit_library(request, pk):
    library = get_object_or_404(Library, pk=pk)
    
    # Erişim kontrolü
    if not (request.user.is_super_admin() or library.owner == request.user):
        return HttpResponseForbidden("Bu kütüphaneyi düzenleme izniniz yok.")
    
    if request.method == 'POST':
        form = LibraryForm(request.POST, instance=library)
        if form.is_valid():
            form.save()
            messages.success(request, 'Kütüphane başarıyla güncellendi!')
            return redirect('library_detail', pk=library.pk)
    else:
        form = LibraryForm(instance=library)
    
    return render(request, 'libraries/library_form.html', {'form': form, 'title': 'Kütüphaneyi Düzenle'})

@login_required
def delete_library(request, pk):
    library = get_object_or_404(Library, pk=pk)
    
    # Erişim kontrolü
    if not (request.user.is_super_admin() or library.owner == request.user):
        return HttpResponseForbidden("Bu kütüphaneyi silme izniniz yok.")
    
    if request.method == 'POST':
        library.delete()
        messages.success(request, 'Kütüphane başarıyla silindi!')
        return redirect('library_list')
    
    return render(request, 'libraries/library_confirm_delete.html', {'library': library})
