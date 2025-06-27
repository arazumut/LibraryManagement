from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from books.models import Book
from books.models_collection import BookCollection, BookCollectionItem
from .forms import BookCollectionForm, BookCollectionItemForm
from django.db.models import Q

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
        return redirect('books:collection_list')
    
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
            return redirect('books:collection_detail', collection_id=collection.id)
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
        return redirect('books:collection_list')
    
    if request.method == 'POST':
        form = BookCollectionForm(request.POST, request.FILES, instance=collection)
        if form.is_valid():
            form.save()
            messages.success(request, 'Koleksiyon başarıyla güncellendi.')
            return redirect('books:collection_detail', collection_id=collection.id)
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
        return redirect('books:collection_list')
    
    if request.method == 'POST':
        collection.delete()
        messages.success(request, 'Koleksiyon başarıyla silindi.')
        return redirect('books:collection_list')
    
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
        return redirect('books:collection_detail', collection_id=collection.id)
    
    # Koleksiyonda zaten bulunan kitapları dışla
    existing_books = BookCollectionItem.objects.filter(
        collection=collection
    ).values_list('book_id', flat=True)
    
    # AJAX Kitap arama isteği
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and 'term' in request.GET:
        term = request.GET.get('term', '')
        books = Book.objects.filter(
            Q(title__icontains=term) | Q(author__icontains=term),
            status='available'
        ).exclude(id__in=existing_books).order_by('title')[:20]
        
        results = []
        for book in books:
            results.append({
                'id': book.id,
                'text': f"{book.title} - {book.author}"
            })
        
        return JsonResponse({'results': results})
    
    if request.method == 'POST':
        form = BookCollectionItemForm(request.POST)
        # Mevcut kitapları formun queryset'inden çıkar
        form.fields['book'].queryset = Book.objects.filter(
            status='available'
        ).exclude(id__in=existing_books).order_by('title')
        
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
            
            return redirect('books:collection_detail', collection_id=collection.id)
    else:
        form = BookCollectionItemForm()
        # Mevcut kitapları formun queryset'inden çıkar
        form.fields['book'].queryset = Book.objects.filter(
            status='available'
        ).exclude(id__in=existing_books).order_by('title')
    
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
        return redirect('books:collection_detail', collection_id=collection.id)
    
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Kitap başarıyla koleksiyondan çıkarıldı.')
        return redirect('books:collection_detail', collection_id=collection.id)
    
    return render(request, 'books/collection_remove_book.html', {
        'item': item,
        'collection': collection,
    })

@login_required
def collection_analytics(request, collection_id):
    """Koleksiyon analitikleri."""
    collection = get_object_or_404(BookCollection, id=collection_id, owner=request.user)
    
    # Koleksiyon istatistikleri
    total_books = collection.book_count
    completed_books = collection.completed_books_count
    reading_progress = collection.reading_progress
    
    # Kategori dağılımı
    category_stats = {}
    for item in collection.bookcollectionitem_set.all():
        for book_category in item.book.categories.all():
            category = book_category.category
            if category.name not in category_stats:
                category_stats[category.name] = 0
            category_stats[category.name] += 1
    
    # Okuma durumu dağılımı
    status_stats = {}
    for item in collection.bookcollectionitem_set.all():
        status = item.get_reading_status_display()
        if status not in status_stats:
            status_stats[status] = 0
        status_stats[status] += 1
    
    context = {
        'collection': collection,
        'total_books': total_books,
        'completed_books': completed_books,
        'reading_progress': reading_progress,
        'category_stats': category_stats,
        'status_stats': status_stats,
    }
    
    return render(request, 'books/collection_analytics.html', context)

@login_required
def collection_share(request, collection_id):
    """Koleksiyonu paylaş."""
    collection = get_object_or_404(BookCollection, id=collection_id, owner=request.user)
    
    if request.method == 'POST':
        visibility = request.POST.get('visibility')
        if visibility in ['public', 'private', 'friends']:
            collection.visibility = visibility
            collection.save()
            messages.success(request, f'Koleksiyon görünürlüğü {collection.get_visibility_display()} olarak güncellendi.')
        return redirect('books:collection_detail', collection_id=collection.id)
    
    return render(request, 'books/collection_share.html', {
        'collection': collection,
    })

@login_required
def collection_export(request, collection_id):
    """Koleksiyonu dışa aktar."""
    collection = get_object_or_404(BookCollection, id=collection_id, owner=request.user)
    
    format_type = request.GET.get('format', 'json')
    
    if format_type == 'json':
        import json
        from django.http import HttpResponse
        
        collection_data = {
            'name': collection.name,
            'description': collection.description,
            'created_at': collection.created_at.isoformat(),
            'books': []
        }
        
        for item in collection.bookcollectionitem_set.all():
            book_data = {
                'title': item.book.title,
                'author': item.book.author,
                'isbn': item.book.isbn,
                'added_at': item.added_at.isoformat(),
                'notes': item.notes,
                'rating': item.rating,
                'reading_status': item.reading_status,
                'progress_percentage': item.progress_percentage,
            }
            collection_data['books'].append(book_data)
        
        response = HttpResponse(
            json.dumps(collection_data, indent=2, ensure_ascii=False),
            content_type='application/json; charset=utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename="{collection.name}_collection.json"'
        return response
    
    elif format_type == 'csv':
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="{collection.name}_collection.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Başlık', 'Yazar', 'ISBN', 'Eklenme Tarihi', 'Notlar', 'Puan', 'Okuma Durumu', 'İlerleme %'])
        
        for item in collection.bookcollectionitem_set.all():
            writer.writerow([
                item.book.title,
                item.book.author,
                item.book.isbn or '',
                item.added_at.strftime('%Y-%m-%d'),
                item.notes or '',
                item.rating or '',
                item.get_reading_status_display(),
                item.progress_percentage,
            ])
        
        return response
    
    return redirect('books:collection_detail', collection_id=collection.id)

@login_required  
def collection_follow(request, collection_id):
    """Koleksiyonu takip et/takibi bırak."""
    from books.models_collection import CollectionFollow
    
    collection = get_object_or_404(BookCollection, id=collection_id)
    
    if collection.owner == request.user:
        return JsonResponse({'error': 'Kendi koleksiyonunuzu takip edemezsiniz.'}, status=400)
    
    if collection.visibility != 'public':
        return JsonResponse({'error': 'Bu koleksiyonu takip edemezsiniz.'}, status=400)
    
    follow, created = CollectionFollow.objects.get_or_create(
        follower=request.user,
        collection=collection
    )
    
    if not created:
        follow.delete()
        action = 'unfollowed'
    else:
        action = 'followed'
    
    follower_count = collection.followers.count()
    
    return JsonResponse({
        'action': action,
        'follower_count': follower_count,
        'is_following': action == 'followed'
    })

@login_required
def my_followed_collections(request):
    """Takip edilen koleksiyonlar."""
    from books.models_collection import CollectionFollow
    
    followed_collections = CollectionFollow.objects.filter(
        follower=request.user
    ).select_related('collection', 'collection__owner')
    
    return render(request, 'books/followed_collections.html', {
        'followed_collections': followed_collections,
    })
