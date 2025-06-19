from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from books.models import Book
from books.models_collection import BookCollection, BookCollectionItem
from .forms import BookCollectionForm, BookCollectionItemForm

@login_required
def collection_list(request):
    """Kullanıcının koleksiyonlarını listele."""
    # Kullanıcının kendi koleksiyonları
    user_collections = BookCollection.objects.filter(owner=request.user)
    
    # Herkese açık diğer koleksiyonlar
    public_collections = BookCollection.objects.filter(visibility='public').exclude(owner=request.user)
    
    return render(request, 'books/collection_list.html', {
        'user_collections': user_collections,
        'public_collections': public_collections,
    })

@login_required
def collection_detail(request, collection_id):
    """Koleksiyon detaylarını göster."""
    collection = get_object_or_404(BookCollection, id=collection_id)
    
    # Koleksiyonu görüntüleme yetkisi kontrol et
    if collection.visibility == 'private' and collection.owner != request.user:
        messages.error(request, 'Bu koleksiyonu görüntüleme yetkiniz yok.')
        return redirect('collection_list')
    
    # Koleksiyondaki kitaplar
    collection_items = collection.bookcollectionitem_set.all().select_related('book')
    
    return render(request, 'books/collection_detail.html', {
        'collection': collection,
        'collection_items': collection_items,
        'is_owner': collection.owner == request.user,
    })

@login_required
def collection_create(request):
    """Yeni koleksiyon oluştur."""
    if request.method == 'POST':
        form = BookCollectionForm(request.POST, request.FILES)
        if form.is_valid():
            collection = form.save(commit=False)
            collection.owner = request.user
            collection.save()
            messages.success(request, 'Koleksiyon başarıyla oluşturuldu.')
            return redirect('collection_detail', collection_id=collection.id)
    else:
        form = BookCollectionForm()
    
    return render(request, 'books/collection_form.html', {
        'form': form,
        'is_edit': False,
    })

@login_required
def collection_edit(request, collection_id):
    """Koleksiyonu düzenle."""
    collection = get_object_or_404(BookCollection, id=collection_id)
    
    # Sadece sahip düzenleyebilir
    if collection.owner != request.user:
        messages.error(request, 'Bu koleksiyonu düzenleme yetkiniz yok.')
        return redirect('collection_list')
    
    if request.method == 'POST':
        form = BookCollectionForm(request.POST, request.FILES, instance=collection)
        if form.is_valid():
            form.save()
            messages.success(request, 'Koleksiyon başarıyla güncellendi.')
            return redirect('collection_detail', collection_id=collection.id)
    else:
        form = BookCollectionForm(instance=collection)
    
    return render(request, 'books/collection_form.html', {
        'form': form,
        'collection': collection,
        'is_edit': True,
    })

@login_required
def collection_delete(request, collection_id):
    """Koleksiyonu sil."""
    collection = get_object_or_404(BookCollection, id=collection_id)
    
    # Sadece sahip silebilir
    if collection.owner != request.user:
        messages.error(request, 'Bu koleksiyonu silme yetkiniz yok.')
        return redirect('collection_list')
    
    if request.method == 'POST':
        collection.delete()
        messages.success(request, 'Koleksiyon başarıyla silindi.')
        return redirect('collection_list')
    
    return render(request, 'books/collection_confirm_delete.html', {
        'collection': collection,
    })

@login_required
def collection_add_book(request, collection_id):
    """Koleksiyona kitap ekle."""
    collection = get_object_or_404(BookCollection, id=collection_id)
    
    # Sadece sahip kitap ekleyebilir
    if collection.owner != request.user:
        messages.error(request, 'Bu koleksiyona kitap ekleme yetkiniz yok.')
        return redirect('collection_detail', collection_id=collection.id)
    
    if request.method == 'POST':
        form = BookCollectionItemForm(request.POST)
        if form.is_valid():
            book = form.cleaned_data['book']
            notes = form.cleaned_data['notes']
            
            # Kitap zaten koleksiyonda mı kontrol et
            if BookCollectionItem.objects.filter(collection=collection, book=book).exists():
                messages.warning(request, 'Bu kitap zaten koleksiyonunuzda bulunuyor.')
            else:
                # Yeni kitap ekle
                item = BookCollectionItem(collection=collection, book=book, notes=notes)
                item.save()
                messages.success(request, 'Kitap başarıyla koleksiyona eklendi.')
            
            return redirect('collection_detail', collection_id=collection.id)
    else:
        form = BookCollectionItemForm()
    
    return render(request, 'books/collection_add_book.html', {
        'form': form,
        'collection': collection,
    })

@login_required
def collection_remove_book(request, collection_id, item_id):
    """Koleksiyondan kitap çıkar."""
    collection = get_object_or_404(BookCollection, id=collection_id)
    item = get_object_or_404(BookCollectionItem, id=item_id, collection=collection)
    
    # Sadece sahip kitap çıkarabilir
    if collection.owner != request.user:
        messages.error(request, 'Bu koleksiyondan kitap çıkarma yetkiniz yok.')
        return redirect('collection_detail', collection_id=collection.id)
    
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Kitap başarıyla koleksiyondan çıkarıldı.')
        return redirect('collection_detail', collection_id=collection.id)
    
    return render(request, 'books/collection_remove_book.html', {
        'item': item,
        'collection': collection,
    })
