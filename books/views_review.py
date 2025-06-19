from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from books.models import Book
from books.models_review import BookReview, BookReviewLike
from .forms import BookReviewForm

@login_required
def book_review_create(request, book_id):
    """Kitap için yeni değerlendirme oluşturma."""
    book = get_object_or_404(Book, id=book_id)
    
    # Kullanıcının daha önce bu kitap için değerlendirme yapıp yapmadığını kontrol et
    existing_review = BookReview.objects.filter(book=book, user=request.user).first()
    if existing_review:
        messages.warning(request, 'Bu kitap için zaten bir değerlendirme yapmışsınız. Değerlendirmenizi düzenleyebilirsiniz.')
        return redirect('book_review_edit', review_id=existing_review.id)
    
    if request.method == 'POST':
        form = BookReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.book = book
            review.user = request.user
            review.save()
            messages.success(request, 'Değerlendirmeniz başarıyla kaydedildi.')
            return redirect('book_detail', pk=book.id)
    else:
        form = BookReviewForm()
    
    return render(request, 'books/review_form.html', {
        'form': form,
        'book': book,
        'is_edit': False,
    })

@login_required
def book_review_edit(request, review_id):
    """Kitap değerlendirmesini düzenleme."""
    review = get_object_or_404(BookReview, id=review_id)
    
    # Sadece değerlendirmeyi yapan kişi düzenleyebilir
    if review.user != request.user:
        messages.error(request, 'Bu değerlendirmeyi düzenleme yetkiniz yok.')
        return redirect('book_detail', pk=review.book.id)
    
    if request.method == 'POST':
        form = BookReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'Değerlendirmeniz başarıyla güncellendi.')
            return redirect('book_detail', pk=review.book.id)
    else:
        form = BookReviewForm(instance=review)
    
    return render(request, 'books/review_form.html', {
        'form': form,
        'book': review.book,
        'review': review,
        'is_edit': True,
    })

@login_required
def book_review_delete(request, review_id):
    """Kitap değerlendirmesini silme."""
    review = get_object_or_404(BookReview, id=review_id)
    
    # Sadece değerlendirmeyi yapan kişi veya yönetici silebilir
    if review.user != request.user and not request.user.is_staff:
        messages.error(request, 'Bu değerlendirmeyi silme yetkiniz yok.')
        return redirect('book_detail', pk=review.book.id)
    
    if request.method == 'POST':
        book_id = review.book.id
        review.delete()
        messages.success(request, 'Değerlendirmeniz başarıyla silindi.')
        return redirect('book_detail', pk=book_id)
    
    return render(request, 'books/review_confirm_delete.html', {
        'review': review,
    })

@login_required
def book_review_like_toggle(request, review_id):
    """Kitap değerlendirmesini beğenme/beğenmeme."""
    if request.method == 'POST':
        review = get_object_or_404(BookReview, id=review_id)
        
        # Kendini beğenmesini engelle
        if review.user == request.user:
            messages.warning(request, 'Kendi değerlendirmenizi beğenemezsiniz.')
        else:
            # Daha önce beğenilmiş mi kontrol et
            like = BookReviewLike.objects.filter(review=review, user=request.user).first()
            
            if like:
                # Beğeniyi kaldır
                like.delete()
                messages.success(request, 'Değerlendirmeyi beğenmekten vazgeçtiniz.')
            else:
                # Beğeni ekle
                BookReviewLike.objects.create(review=review, user=request.user)
                messages.success(request, 'Değerlendirmeyi beğendiniz.')
        
        # Sayfa başına dön
        return redirect(request.META.get('HTTP_REFERER', 'book_detail', pk=review.book.id))
    
    # POST değilse, yönlendir
    return redirect('home')

@login_required
def book_review_list(request):
    """Tüm kitap değerlendirmeleri."""
    reviews = BookReview.objects.all().order_by('-created_at')
    
    return render(request, 'books/review_list.html', {
        'reviews': reviews,
        'active_menu': 'reviews',
    })
