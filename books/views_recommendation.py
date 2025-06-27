from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import timedelta
import random

from books.models import Book
from books.models_recommendation import (
    AIAIBookRecommendation, 
    UserReadingProfile, 
    CategoryPreference,
    RecommendationFeedback
)
from books.models_category import Category
from loans.models import Loan
from books.models_review import BookReview

@login_required
def recommendation_dashboard(request):
    """Öneri dashboard'u."""
    # Kullanıcının okuma profilini al veya oluştur
    reading_profile, created = UserReadingProfile.objects.get_or_create(
        user=request.user
    )
    
    if created or not reading_profile.last_recommendation_date:
        # İlk kez gelen kullanıcı için profil güncelle
        reading_profile.update_preferences()
    
    # Bekleyen önerileri al
    pending_recommendations = AIBookRecommendation.objects.filter(
        user=request.user,
        status='pending'
    ).select_related('book')[:6]
    
    # Öneriler yoksa yeni öneriler oluştur
    if not pending_recommendations.exists():
        generate_recommendations_for_user(request.user)
        pending_recommendations = AIBookRecommendation.objects.filter(
            user=request.user,
            status='pending'
        ).select_related('book')[:6]
    
    # Son aktiviteler
    recent_recommendations = AIBookRecommendation.objects.filter(
        user=request.user
    ).exclude(status='pending').order_by('-created_at')[:10]
    
    # İstatistikler
    total_recommendations = AIBookRecommendation.objects.filter(user=request.user).count()
    liked_count = AIBookRecommendation.objects.filter(user=request.user, status='liked').count()
    borrowed_count = AIBookRecommendation.objects.filter(user=request.user, status='borrowed').count()
    
    context = {
        'reading_profile': reading_profile,
        'pending_recommendations': pending_recommendations,
        'recent_recommendations': recent_recommendations,
        'total_recommendations': total_recommendations,
        'liked_count': liked_count,
        'borrowed_count': borrowed_count,
        'active_menu': 'recommendations',
    }
    
    return render(request, 'books/recommendation_dashboard.html', context)

@login_required
def recommendation_respond(request, recommendation_id):
    """Öneriye yanıt ver."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)
    
    recommendation = get_object_or_404(
        AIBookRecommendation, 
        id=recommendation_id, 
        user=request.user
    )
    
    response_type = request.POST.get('response')
    
    if response_type in ['liked', 'disliked', 'saved']:
        recommendation.mark_response(response_type)
        
        # Geri bildirim oluştur
        if response_type in ['liked', 'disliked']:
            rating = 5 if response_type == 'liked' else 1
            RecommendationFeedback.objects.get_or_create(
                user=request.user,
                recommendation=recommendation,
                feedback_type='relevance',
                defaults={'rating': rating}
            )
        
        return JsonResponse({
            'status': 'success',
            'message': f'Öneri {response_type} olarak işaretlendi.',
            'new_status': recommendation.status
        })
    
    return JsonResponse({'error': 'Invalid response type'}, status=400)

@login_required
def view_recommendation(request, recommendation_id):
    """Öneriyi görüntüle ve kitap detayına yönlendir."""
    recommendation = get_object_or_404(
        AIBookRecommendation, 
        id=recommendation_id, 
        user=request.user
    )
    
    # Öneriyi görüntülendi olarak işaretle
    recommendation.mark_as_viewed()
    
    # Kitap detay sayfasına yönlendir
    return redirect('books:detail', book_id=recommendation.book.id)

@login_required
def recommendation_settings(request):
    """Öneri ayarları."""
    reading_profile, created = UserReadingProfile.objects.get_or_create(
        user=request.user
    )
    
    if request.method == 'POST':
        # Ayarları güncelle
        frequency = request.POST.get('recommendation_frequency')
        if frequency in ['daily', 'weekly', 'monthly', 'never']:
            reading_profile.recommendation_frequency = frequency
        
        preferred_length = request.POST.get('preferred_book_length')
        if preferred_length in ['short', 'medium', 'long', 'any']:
            reading_profile.preferred_book_length = preferred_length
        
        # Favori kategorileri güncelle
        selected_categories = request.POST.getlist('favorite_categories')
        if selected_categories:
            # Mevcut tercihleri temizle
            CategoryPreference.objects.filter(reading_profile=reading_profile).delete()
            
            # Yeni tercihleri ekle
            for cat_id in selected_categories:
                try:
                    category = Category.objects.get(id=cat_id)
                    CategoryPreference.objects.create(
                        reading_profile=reading_profile,
                        category=category,
                        weight=1.0
                    )
                except Category.DoesNotExist:
                    pass
        
        reading_profile.save()
        messages.success(request, 'Öneri ayarlarınız güncellendi.')
        return redirect('books:recommendation_settings')
    
    # Tüm kategoriler
    all_categories = Category.objects.all().order_by('name')
    
    # Kullanıcının mevcut kategori tercihleri
    current_categories = reading_profile.favorite_categories.all()
    
    context = {
        'reading_profile': reading_profile,
        'all_categories': all_categories,
        'current_categories': current_categories,
        'active_menu': 'recommendations',
    }
    
    return render(request, 'books/recommendation_settings.html', context)

@login_required
def generate_new_recommendations(request):
    """Yeni öneriler oluştur."""
    if request.method == 'POST':
        # Mevcut bekleyen önerileri sil
        AIBookRecommendation.objects.filter(
            user=request.user, 
            status='pending'
        ).delete()
        
        # Yeni öneriler oluştur
        count = generate_recommendations_for_user(request.user)
        
        messages.success(request, f'{count} yeni öneri oluşturuldu.')
        return JsonResponse({'status': 'success', 'count': count})
    
    return JsonResponse({'error': 'Invalid method'}, status=405)

def generate_recommendations_for_user(user, limit=10):
    """Kullanıcı için öneriler oluştur."""
    recommendations_created = 0
    
    # Kullanıcının okuma profilini al
    try:
        reading_profile = user.reading_profile
    except:
        reading_profile = UserReadingProfile.objects.create(user=user)
        reading_profile.update_preferences()
    
    # Kullanıcının daha önce ödünç aldığı kitapları al
    user_books = set(
        Loan.objects.filter(borrower=user).values_list('book_id', flat=True)
    )
    
    # Zaten önerilmiş kitapları al
    recommended_books = set(
        AIBookRecommendation.objects.filter(user=user).values_list('book_id', flat=True)
    )
    
    # Önerilecek kitapları bul
    excluded_books = user_books.union(recommended_books)
    
    # 1. Kategori tabanlı öneriler
    favorite_categories = reading_profile.favorite_categories.all()
    if favorite_categories.exists():
        category_books = Book.objects.filter(
            categories__category__in=favorite_categories,
            status='available'
        ).exclude(id__in=excluded_books).distinct()[:5]
        
        for book in category_books:
            recommendation = AIBookRecommendation.objects.create(
                user=user,
                book=book,
                recommendation_type='category_based',
                confidence_score=0.8,
                reason=f"Bu kitap favori kategorilerinizden birinde: {book.categories.first().category.name if book.categories.exists() else ''}"
            )
            recommendations_created += 1
    
    # 2. Popüler kitap önerileri
    popular_books = Book.objects.filter(
        status='available'
    ).exclude(id__in=excluded_books).annotate(
        loan_count=Count('loans')
    ).order_by('-loan_count')[:3]
    
    for book in popular_books:
        AIBookRecommendation.objects.create(
            user=user,
            book=book,
            recommendation_type='trending',
            confidence_score=0.6,
            reason="Bu kitap kütüphanede çok popüler!"
        )
        recommendations_created += 1
    
    # 3. Yeni çıkan kitaplar
    thirty_days_ago = timezone.now() - timedelta(days=30)
    new_books = Book.objects.filter(
        created_at__gte=thirty_days_ago,
        status='available'
    ).exclude(id__in=excluded_books)[:2]
    
    for book in new_books:
        AIBookRecommendation.objects.create(
            user=user,
            book=book,
            recommendation_type='new_releases',
            confidence_score=0.5,
            reason="Bu kitap kütüphaneye yeni eklendi!"
        )
        recommendations_created += 1
    
    # Son güncelleme tarihini ayarla
    reading_profile.last_recommendation_date = timezone.now()
    reading_profile.save()
    
    return recommendations_created

@login_required
def recommendation_feedback(request, recommendation_id):
    """Öneri geri bildirimi."""
    recommendation = get_object_or_404(
        AIBookRecommendation, 
        id=recommendation_id, 
        user=request.user
    )
    
    if request.method == 'POST':
        feedback_type = request.POST.get('feedback_type')
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        if feedback_type and rating:
            RecommendationFeedback.objects.update_or_create(
                user=request.user,
                recommendation=recommendation,
                feedback_type=feedback_type,
                defaults={
                    'rating': int(rating),
                    'comment': comment
                }
            )
            
            messages.success(request, 'Geri bildiriminiz kaydedildi.')
            return JsonResponse({'status': 'success'})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def discover_books(request):
    """Kitap keşfet sayfası."""
    # Rastgele kategorilerden kitaplar
    categories = Category.objects.filter(is_featured=True)[:6]
    category_books = {}
    
    for category in categories:
        books = Book.objects.filter(
            categories__category=category,
            status='available'
        ).distinct()[:4]
        if books:
            category_books[category] = books
    
    # Yeni eklenen kitaplar
    new_books = Book.objects.filter(
        status='available'
    ).order_by('-created_at')[:8]
    
    # En çok ödünç verilen kitaplar
    popular_books = Book.objects.filter(
        status='available'
    ).annotate(
        loan_count=Count('loans')
    ).order_by('-loan_count')[:8]
    
    # En yüksek puanlı kitaplar
    top_rated_books = Book.objects.filter(
        status='available'
    ).annotate(
        avg_rating=Avg('reviews__rating')
    ).filter(avg_rating__isnull=False).order_by('-avg_rating')[:8]
    
    context = {
        'category_books': category_books,
        'new_books': new_books,
        'popular_books': popular_books,
        'top_rated_books': top_rated_books,
        'active_menu': 'discover',
    }
    
    return render(request, 'books/discover.html', context)
