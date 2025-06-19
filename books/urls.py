from django.urls import path
from . import views
from . import views_review, views_collection, views_reservation, views_goals

app_name = 'books'

urlpatterns = [
    # Temel kitap işlemleri
    path('', views.book_list, name='list'),
    path('<int:book_id>/', views.book_detail, name='detail'),
    path('create/', views.book_create, name='create'),
    path('<int:book_id>/edit/', views.book_edit, name='edit'),
    path('<int:book_id>/delete/', views.book_delete, name='delete'),
    path('requests/', views.book_requests, name='requests'),
    path('requests/create/', views.book_request_create, name='request_create'),
    path('requests/<int:request_id>/cancel/', views.book_request_cancel, name='request_cancel'),
    path('requests/<int:request_id>/approve/', views.book_request_approve, name='request_approve'),
    path('requests/<int:request_id>/reject/', views.book_request_reject, name='request_reject'),
    
    # Değerlendirme ve yorum sistemi
    path('<int:book_id>/review/create/', views_review.book_review_create, name='review_create'),
    path('review/<int:review_id>/edit/', views_review.book_review_edit, name='review_edit'),
    path('review/<int:review_id>/delete/', views_review.book_review_delete, name='review_delete'),
    path('review/<int:review_id>/like/', views_review.book_review_like_toggle, name='review_like'),
    path('reviews/', views_review.book_review_list, name='review_list'),
    
    # Koleksiyon sistemi
    path('collections/', views_collection.collection_list, name='collection_list'),
    path('collections/create/', views_collection.collection_create, name='collection_create'),
    path('collections/<int:collection_id>/', views_collection.collection_detail, name='collection_detail'),
    path('collections/<int:collection_id>/edit/', views_collection.collection_edit, name='collection_edit'),
    path('collections/<int:collection_id>/delete/', views_collection.collection_delete, name='collection_delete'),
    path('collections/<int:collection_id>/add-book/', views_collection.collection_add_book, name='collection_add_book'),
    path('collections/<int:collection_id>/remove-book/<int:item_id>/', views_collection.collection_remove_book, name='collection_remove_book'),
    
    # Rezervasyon sistemi
    path('reservations/', views_reservation.reservation_list, name='reservation_list'),
    path('<int:book_id>/reserve/', views_reservation.reservation_create, name='reservation_create'),
    path('reservations/<int:reservation_id>/', views_reservation.reservation_detail, name='reservation_detail'),
    path('reservations/<int:reservation_id>/cancel/', views_reservation.reservation_cancel, name='reservation_cancel'),
    path('reservations/<int:reservation_id>/fulfill/', views_reservation.reservation_fulfill, name='reservation_fulfill'),
    path('<int:book_id>/notify-reservations/', views_reservation.book_return_notify_reservations, name='notify_reservations'),
    
    # Okuma hedefleri
    path('goals/', views_goals.goal_list, name='goal_list'),
    path('goals/create/', views_goals.goal_create, name='goal_create'),
    path('goals/<int:goal_id>/', views_goals.goal_detail, name='goal_detail'),
    path('goals/<int:goal_id>/edit/', views_goals.goal_update, name='goal_edit'),
    path('goals/<int:goal_id>/delete/', views_goals.goal_delete, name='goal_delete'),
    path('goals/<int:goal_id>/progress/', views_goals.goal_update_progress, name='goal_progress'),
]
