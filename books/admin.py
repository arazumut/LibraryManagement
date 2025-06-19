from django.contrib import admin
from .models import Book, BookRequest
from .models_review import BookReview, BookReviewLike
from .models_collection import BookCollection, BookCollectionItem
from .models_category import Category, BookCategory, Tag, BookTag
from .models_goals import ReadingGoal, ReadingChallenge, ChallengeParticipant
from .models_identifier import BookIdentifier, ScanRecord
from .models_reservation import BookReservation

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'isbn', 'library', 'status', 'publication_year')
    list_filter = ('status', 'library', 'language', 'publication_year')
    search_fields = ('title', 'author', 'isbn', 'publisher', 'description')
    date_hierarchy = 'created_at'

@admin.register(BookRequest)
class BookRequestAdmin(admin.ModelAdmin):
    list_display = ('book', 'requester', 'status', 'requested_at')
    list_filter = ('status',)
    search_fields = ('book__title', 'requester__username', 'message')
    date_hierarchy = 'requested_at'

# Değerlendirme ve Yorum Sistemi
@admin.register(BookReview)
class BookReviewAdmin(admin.ModelAdmin):
    list_display = ('book', 'user', 'rating', 'created_at', 'is_public')
    list_filter = ('rating', 'is_public', 'created_at')
    search_fields = ('book__title', 'user__username', 'review_text')
    date_hierarchy = 'created_at'

@admin.register(BookReviewLike)
class BookReviewLikeAdmin(admin.ModelAdmin):
    list_display = ('review', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('review__review_text', 'user__username')
    date_hierarchy = 'created_at'

# Koleksiyon Sistemi
@admin.register(BookCollection)
class BookCollectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'visibility', 'created_at', 'is_featured')
    list_filter = ('visibility', 'is_featured', 'created_at')
    search_fields = ('name', 'owner__username', 'description')
    date_hierarchy = 'created_at'

@admin.register(BookCollectionItem)
class BookCollectionItemAdmin(admin.ModelAdmin):
    list_display = ('book', 'collection', 'added_at', 'order')
    list_filter = ('added_at',)
    search_fields = ('book__title', 'collection__name', 'notes')

# Kategori ve Etiket Sistemi
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'slug')
    list_filter = ('created_at',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(BookCategory)
class BookCategoryAdmin(admin.ModelAdmin):
    list_display = ('book', 'category', 'created_at')
    list_filter = ('created_at', 'category')
    search_fields = ('book__title', 'category__name')

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(BookTag)
class BookTagAdmin(admin.ModelAdmin):
    list_display = ('book', 'tag', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('book__title', 'tag__name')

# Okuma Hedefleri ve Meydan Okumalar
@admin.register(ReadingGoal)
class ReadingGoalAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'goal_type', 'target_value', 'current_value', 'is_completed', 'period')
    list_filter = ('goal_type', 'period', 'is_completed', 'is_public')
    search_fields = ('title', 'user__username', 'description')
    date_hierarchy = 'start_date'

@admin.register(ReadingChallenge)
class ReadingChallengeAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'start_date', 'end_date', 'goal_type', 'target_value', 'status')
    list_filter = ('status', 'goal_type', 'is_featured', 'is_private')
    search_fields = ('title', 'creator__username', 'description')
    date_hierarchy = 'start_date'

@admin.register(ChallengeParticipant)
class ChallengeParticipantAdmin(admin.ModelAdmin):
    list_display = ('user', 'challenge', 'current_value', 'is_completed', 'joined_at')
    list_filter = ('is_completed', 'joined_at')
    search_fields = ('user__username', 'challenge__title')
    date_hierarchy = 'joined_at'

# QR Kod ve Barkod Sistemi
@admin.register(BookIdentifier)
class BookIdentifierAdmin(admin.ModelAdmin):
    list_display = ('book', 'identifier_type', 'value', 'is_active', 'created_at')
    list_filter = ('identifier_type', 'is_active', 'created_at')
    search_fields = ('book__title', 'value')
    date_hierarchy = 'created_at'

@admin.register(ScanRecord)
class ScanRecordAdmin(admin.ModelAdmin):
    list_display = ('identifier', 'user', 'scan_date', 'scan_type', 'location')
    list_filter = ('scan_date', 'scan_type')
    search_fields = ('identifier__value', 'user__username', 'location')
    date_hierarchy = 'scan_date'

# Rezervasyon Sistemi
@admin.register(BookReservation)
class BookReservationAdmin(admin.ModelAdmin):
    list_display = ('book', 'user', 'status', 'reservation_date', 'notification_date', 'expiry_date')
    list_filter = ('status', 'reservation_date')
    search_fields = ('book__title', 'user__username')
    date_hierarchy = 'reservation_date'
