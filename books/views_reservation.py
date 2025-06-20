from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from books.models import Book
from books.models_reservation import BookReservation
from django.utils import timezone
from django.db.models import Q

@login_required
def reservation_list(request):
    """Kullanıcının rezervasyonlarını listele."""
    # Kullanıcının aktif rezervasyonları
    active_reservations = BookReservation.objects.filter(
        user=request.user,
        status__in=['pending', 'notified']
    ).select_related('book')
    
    # Kullanıcının geçmiş rezervasyonları
    past_reservations = BookReservation.objects.filter(
        user=request.user,
        status__in=['fulfilled', 'expired', 'cancelled']
    ).select_related('book')
    
    return render(request, 'books/reservation_list.html', {
        'active_reservations': active_reservations,
        'past_reservations': past_reservations,
    })

@login_required
def reservation_create(request, book_id):
    """Kitap için rezervasyon oluştur."""
    book = get_object_or_404(Book, id=book_id)
    
    # Kitap zaten müsait mi kontrol et
    if book.status == 'available':
        messages.info(request, 'Bu kitap zaten müsait, doğrudan ödünç alabilirsiniz.')
        return redirect('books:detail', pk=book.id)
    
    # Kullanıcının bu kitap için zaten aktif bir rezervasyonu var mı kontrol et
    existing_reservation = BookReservation.objects.filter(
        book=book,
        user=request.user,
        status__in=['pending', 'notified']
    ).first()
    
    if existing_reservation:
        messages.warning(request, 'Bu kitap için zaten bir rezervasyonunuz bulunuyor.')
        return redirect('books:reservation_detail', reservation_id=existing_reservation.id)
    
    # Yeni rezervasyon oluştur
    reservation = BookReservation(
        book=book,
        user=request.user
    )
    reservation.save()
    
    messages.success(request, 'Kitap başarıyla rezerve edildi. Müsait olduğunda bildirim alacaksınız.')
    return redirect('books:reservation_detail', reservation_id=reservation.id)

@login_required
def reservation_detail(request, reservation_id):
    """Rezervasyon detaylarını göster."""
    reservation = get_object_or_404(BookReservation, id=reservation_id)
    
    # Sadece rezervasyonu yapan kişi veya kütüphane yöneticisi görüntüleyebilir
    if reservation.user != request.user and not request.user.is_library_admin:
        messages.error(request, 'Bu rezervasyonu görüntüleme yetkiniz yok.')
        return redirect('books:reservation_list')
    
    return render(request, 'books/reservation_detail.html', {
        'reservation': reservation,
    })

@login_required
def reservation_cancel(request, reservation_id):
    """Rezervasyonu iptal et."""
    reservation = get_object_or_404(BookReservation, id=reservation_id)
    
    # Sadece rezervasyonu yapan kişi iptal edebilir
    if reservation.user != request.user:
        messages.error(request, 'Bu rezervasyonu iptal etme yetkiniz yok.')
        return redirect('reservation_list')
    
    # Sadece aktif rezervasyonlar iptal edilebilir
    if reservation.status not in ['pending', 'notified']:
        messages.error(request, 'Bu rezervasyon zaten tamamlanmış veya iptal edilmiş.')
        return redirect('books:reservation_detail', reservation_id=reservation.id)
    
    if request.method == 'POST':
        reservation.cancel()
        messages.success(request, 'Rezervasyonunuz başarıyla iptal edildi.')
        return redirect('books:reservation_list')
    
    return render(request, 'books/reservation_cancel.html', {
        'reservation': reservation,
    })

@login_required
def reservation_fulfill(request, reservation_id):
    """Rezervasyonu tamamla (Yönetici işlemi)."""
    reservation = get_object_or_404(BookReservation, id=reservation_id)
    
    # Sadece kütüphane yöneticisi tamamlayabilir
    if not request.user.is_library_admin:
        messages.error(request, 'Bu işlemi yapmaya yetkiniz yok.')
        return redirect('books:reservation_list')
    
    # Sadece bildirim gönderilmiş rezervasyonlar tamamlanabilir
    if reservation.status != 'notified':
        messages.error(request, 'Bu rezervasyon henüz tamamlanmaya uygun değil.')
        return redirect('books:reservation_detail', reservation_id=reservation.id)
    
    if request.method == 'POST':
        reservation.fulfill()
        messages.success(request, 'Rezervasyon başarıyla tamamlandı.')
        # Burada ödünç verme işlemi için yönlendirme yapılabilir
        return redirect('books:reservation_list')
    
    return render(request, 'books/reservation_fulfill.html', {
        'reservation': reservation,
    })

@login_required
def book_return_notify_reservations(request, book_id):
    """Kitap iade edildiğinde, rezervasyon sırasına göre kullanıcılara bildirim gönder."""
    # Bu fonksiyon genellikle kitap iade işleminden sonra çağrılır
    
    book = get_object_or_404(Book, id=book_id)
    
    # Kitabın müsait olduğundan emin ol
    if book.status != 'available':
        messages.error(request, 'Kitap şu anda müsait değil, rezervasyon bildirimi gönderilemez.')
        return redirect('books:detail', pk=book.id)
    
    # İlk bekleyen rezervasyonu bul
    next_reservation = BookReservation.objects.filter(
        book=book,
        status='pending'
    ).order_by('reservation_date').first()
    
    if next_reservation:
        # Rezervasyon sahibine bildirim gönder
        next_reservation.notify_available()
        
        # Kitabı rezerve olarak işaretle
        book.status = 'reserved'
        book.save()
        
        messages.success(request, f'Kitap için bekleyen rezervasyon sahibine ({next_reservation.user.username}) bildirim gönderildi.')
    else:
        messages.info(request, 'Bu kitap için bekleyen rezervasyon bulunmuyor.')
    
    return redirect('books:detail', pk=book.id)
