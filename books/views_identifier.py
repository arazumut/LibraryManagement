from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Count
from django.utils import timezone
import json
import qrcode
from io import BytesIO
import base64

from books.models import Book
from books.models_identifier import BookIdentifier, ScanRecord, BookLocation
from libraries.models import Library

@login_required
def identifier_list(request):
    """Kitap tanımlayıcıları listesi."""
    # Kullanıcının kütüphanelerindeki kitaplar
    user_libraries = Library.objects.filter(
        Q(owner=request.user) | Q(admins=request.user)
    ).distinct()
    
    # Filtreleme
    search_query = request.GET.get('search', '')
    identifier_type = request.GET.get('type', '')
    library_id = request.GET.get('library', '')
    
    identifiers = BookIdentifier.objects.filter(
        book__library__in=user_libraries,
        is_active=True
    ).select_related('book', 'book__library', 'created_by')
    
    if search_query:
        identifiers = identifiers.filter(
            Q(value__icontains=search_query) |
            Q(book__title__icontains=search_query) |
            Q(book__author__icontains=search_query)
        )
    
    if identifier_type:
        identifiers = identifiers.filter(identifier_type=identifier_type)
    
    if library_id:
        identifiers = identifiers.filter(book__library_id=library_id)
    
    identifiers = identifiers.order_by('-created_at')
    
    # İstatistikler
    total_identifiers = identifiers.count()
    type_stats = BookIdentifier.objects.filter(
        book__library__in=user_libraries,
        is_active=True
    ).values('identifier_type').annotate(count=Count('id'))
    
    context = {
        'identifiers': identifiers,
        'user_libraries': user_libraries,
        'total_identifiers': total_identifiers,
        'type_stats': type_stats,
        'search_query': search_query,
        'selected_type': identifier_type,
        'selected_library': library_id,
        'active_menu': 'qr_codes',
    }
    
    return render(request, 'books/identifier_list.html', context)

@login_required
def identifier_create(request, book_id):
    """Kitap için yeni tanımlayıcı oluştur."""
    book = get_object_or_404(Book, id=book_id)
    
    # Yetki kontrolü
    if not (book.library.owner == request.user or request.user in book.library.admins.all()):
        messages.error(request, 'Bu kitap için tanımlayıcı oluşturma yetkiniz yok.')
        return redirect('books:detail', book_id=book.id)
    
    if request.method == 'POST':
        identifier_type = request.POST.get('identifier_type')
        custom_value = request.POST.get('custom_value', '')
        
        if identifier_type in ['barcode', 'qrcode', 'rfid', 'isbn', 'custom']:
            # Mevcut tanımlayıcı kontrolü
            existing = BookIdentifier.objects.filter(
                book=book,
                identifier_type=identifier_type,
                is_active=True
            ).first()
            
            if existing:
                messages.warning(request, f'Bu kitap için zaten {existing.get_identifier_type_display()} tanımlayıcısı mevcut.')
                return redirect('books:identifier_detail', identifier_id=existing.id)
            
            # Yeni tanımlayıcı oluştur
            identifier = BookIdentifier.objects.create(
                book=book,
                identifier_type=identifier_type,
                value=custom_value if custom_value else None,
                created_by=request.user
            )
            
            messages.success(request, f'{identifier.get_identifier_type_display()} tanımlayıcısı başarıyla oluşturuldu.')
            return redirect('books:identifier_detail', identifier_id=identifier.id)
    
    # Mevcut tanımlayıcılar
    existing_identifiers = BookIdentifier.objects.filter(book=book, is_active=True)
    
    context = {
        'book': book,
        'existing_identifiers': existing_identifiers,
        'identifier_types': BookIdentifier.IDENTIFIER_TYPE_CHOICES,
    }
    
    return render(request, 'books/identifier_create.html', context)

@login_required
def identifier_detail(request, identifier_id):
    """Tanımlayıcı detayları."""
    identifier = get_object_or_404(BookIdentifier, id=identifier_id)
    
    # Yetki kontrolü
    if not (identifier.book.library.owner == request.user or 
            request.user in identifier.book.library.admins.all()):
        messages.error(request, 'Bu tanımlayıcıyı görüntüleme yetkiniz yok.')
        return redirect('books:list')
    
    # Son tarama kayıtları
    recent_scans = ScanRecord.objects.filter(
        identifier=identifier
    ).order_by('-scan_date')[:10]
    
    # Tarama istatistikleri
    total_scans = ScanRecord.objects.filter(identifier=identifier).count()
    unique_users = ScanRecord.objects.filter(identifier=identifier).values('user').distinct().count()
    
    # QR kod resmi oluştur (eğer yoksa)
    if identifier.identifier_type == 'qrcode' and not identifier.qr_code_image:
        identifier.generate_qr_code()
    
    context = {
        'identifier': identifier,
        'recent_scans': recent_scans,
        'total_scans': total_scans,
        'unique_users': unique_users,
    }
    
    return render(request, 'books/identifier_detail.html', context)

@csrf_exempt
@require_http_methods(["POST"])
def scan_identifier(request):
    """QR kod/barkod tarama endpoint'i."""
    try:
        data = json.loads(request.body)
        identifier_value = data.get('identifier')
        scan_action = data.get('action', 'view')
        location = data.get('location', '')
        
        if not identifier_value:
            return JsonResponse({'error': 'Tanımlayıcı değeri gerekli'}, status=400)
        
        # Tanımlayıcıyı bul
        try:
            identifier = BookIdentifier.objects.get(value=identifier_value, is_active=True)
        except BookIdentifier.DoesNotExist:
            return JsonResponse({'error': 'Tanımlayıcı bulunamadı'}, status=404)
        
        # Tarama kaydı oluştur
        scan_record = ScanRecord.objects.create(
            identifier=identifier,
            user=request.user if request.user.is_authenticated else None,
            scan_action=scan_action,
            location=location,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Kitap bilgilerini döndür
        book = identifier.book
        response_data = {
            'success': True,
            'book': {
                'id': book.id,
                'title': book.title,
                'author': book.author,
                'isbn': book.isbn,
                'status': book.status,
                'library': book.library.name,
                'cover_url': book.cover_image.url if book.cover_image else None,
            },
            'identifier': {
                'type': identifier.get_identifier_type_display(),
                'value': identifier.value,
            },
            'scan_id': scan_record.id,
        }
        
        return JsonResponse(response_data)
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Geçersiz JSON verisi'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def qr_code_scanner(request):
    """QR kod tarayıcı sayfası."""
    return render(request, 'books/qr_scanner.html', {
        'active_menu': 'qr_codes',
    })

@login_required
def download_qr_code(request, identifier_id):
    """QR kod resmi indirme."""
    identifier = get_object_or_404(BookIdentifier, id=identifier_id)
    
    # Yetki kontrolü
    if not (identifier.book.library.owner == request.user or 
            request.user in identifier.book.library.admins.all()):
        raise Http404
    
    if identifier.identifier_type != 'qrcode':
        messages.error(request, 'Bu tanımlayıcı bir QR kod değil.')
        return redirect('books:identifier_detail', identifier_id=identifier.id)
    
    # QR kod resmi yoksa oluştur
    if not identifier.qr_code_image:
        identifier.generate_qr_code()
    
    if identifier.qr_code_image:
        response = HttpResponse(identifier.qr_code_image.read(), content_type='image/png')
        response['Content-Disposition'] = f'attachment; filename="{identifier.book.title}_qr.png"'
        return response
    
    messages.error(request, 'QR kod resmi oluşturulamadı.')
    return redirect('books:identifier_detail', identifier_id=identifier.id)

@login_required
def print_qr_codes(request):
    """Seçili QR kodları yazdırma."""
    identifier_ids = request.GET.getlist('ids')
    
    if not identifier_ids:
        messages.error(request, 'Yazdırılacak QR kod seçilmedi.')
        return redirect('books:identifier_list')
    
    # Kullanıcının yetkili olduğu tanımlayıcıları al
    user_libraries = Library.objects.filter(
        Q(owner=request.user) | Q(admins=request.user)
    ).distinct()
    
    identifiers = BookIdentifier.objects.filter(
        id__in=identifier_ids,
        identifier_type='qrcode',
        book__library__in=user_libraries,
        is_active=True
    ).select_related('book')
    
    # QR kod resimlerini oluştur
    for identifier in identifiers:
        if not identifier.qr_code_image:
            identifier.generate_qr_code()
    
    context = {
        'identifiers': identifiers,
    }
    
    return render(request, 'books/print_qr_codes.html', context)

@login_required
def book_location_update(request, book_id):
    """Kitap konum bilgisi güncelleme."""
    book = get_object_or_404(Book, id=book_id)
    
    # Yetki kontrolü
    if not (book.library.owner == request.user or request.user in book.library.admins.all()):
        messages.error(request, 'Bu kitabın konum bilgisini güncelleme yetkiniz yok.')
        return redirect('books:detail', book_id=book.id)
    
    if request.method == 'POST':
        shelf_code = request.POST.get('shelf_code', '')
        section = request.POST.get('section', '')
        floor = request.POST.get('floor', '')
        coordinates = request.POST.get('coordinates', '')
        notes = request.POST.get('notes', '')
        
        # Konum bilgisini al veya oluştur
        location, created = BookLocation.objects.get_or_create(book=book)
        
        # Bilgileri güncelle
        location.update_location(
            user=request.user,
            shelf_code=shelf_code,
            section=section,
            floor=floor,
            coordinates=coordinates,
            notes=notes
        )
        
        messages.success(request, 'Kitap konum bilgisi güncellendi.')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})
        
        return redirect('books:detail', book_id=book.id)
    
    # Mevcut konum bilgisi
    try:
        location = book.location
    except BookLocation.DoesNotExist:
        location = None
    
    context = {
        'book': book,
        'location': location,
    }
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'books/partials/location_form.html', context)
    
    return render(request, 'books/book_location_update.html', context)

@login_required
def scan_statistics(request):
    """Tarama istatistikleri."""
    # Kullanıcının kütüphaneleri
    user_libraries = Library.objects.filter(
        Q(owner=request.user) | Q(admins=request.user)
    ).distinct()
    
    # Son 30 günlük tarama verileri
    from datetime import timedelta
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    recent_scans = ScanRecord.objects.filter(
        identifier__book__library__in=user_libraries,
        scan_date__gte=thirty_days_ago
    )
    
    # İstatistikler
    total_scans = recent_scans.count()
    unique_books = recent_scans.values('identifier__book').distinct().count()
    unique_users = recent_scans.values('user').distinct().count()
    
    # Günlük tarama sayıları
    daily_scans = {}
    for i in range(30):
        date = (timezone.now() - timedelta(days=i)).date()
        count = recent_scans.filter(scan_date__date=date).count()
        daily_scans[date.strftime('%Y-%m-%d')] = count
    
    # En çok taranan kitaplar
    popular_books = recent_scans.values(
        'identifier__book__title',
        'identifier__book__author'
    ).annotate(
        scan_count=Count('id')
    ).order_by('-scan_count')[:10]
    
    # Tarama türleri
    scan_types = recent_scans.values('scan_action').annotate(
        count=Count('id')
    ).order_by('-count')
    
    context = {
        'total_scans': total_scans,
        'unique_books': unique_books,
        'unique_users': unique_users,
        'daily_scans': daily_scans,
        'popular_books': popular_books,
        'scan_types': scan_types,
        'active_menu': 'qr_codes',
    }
    
    return render(request, 'books/scan_statistics.html', context)
