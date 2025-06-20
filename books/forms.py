from django import forms
from books.models_review import BookReview
from books.models_collection import BookCollection
from books.models import Book

class BookReviewForm(forms.ModelForm):
    """Kitap değerlendirme formu."""
    
    class Meta:
        model = BookReview
        fields = ['rating', 'review_text', 'is_public']
        widgets = {
            'rating': forms.Select(choices=[(i, i) for i in range(1, 6)]),
            'review_text': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Kitap hakkındaki düşüncelerinizi paylaşın...'}),
        }
        labels = {
            'rating': 'Değerlendirme (1-5)',
            'review_text': 'Yorum',
            'is_public': 'Herkese açık',
        }
        help_texts = {
            'rating': '1 (En kötü) - 5 (En iyi)',
            'is_public': 'İşaretlerseniz, yorumunuz diğer kullanıcılar tarafından görülebilir.',
        }

class BookCollectionForm(forms.ModelForm):
    """Kitap koleksiyonu oluşturma/düzenleme formu."""
    
    class Meta:
        model = BookCollection
        fields = ['name', 'description', 'visibility', 'cover_image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Koleksiyon hakkında kısa bir açıklama...'}),
        }
        labels = {
            'name': 'Koleksiyon Adı',
            'description': 'Açıklama',
            'visibility': 'Görünürlük',
            'cover_image': 'Kapak Resmi',
        }

class BookCollectionItemForm(forms.Form):
    """Koleksiyona kitap ekleme formu."""
    book = forms.ModelChoiceField(
        queryset=Book.objects.filter(status='available').order_by('title'),
        label='Kitap',
        widget=forms.Select(attrs={
            'class': 'form-control select2-ajax',
            'data-placeholder': 'Kitap arayın...',
            'data-ajax--url': '', # Bu URL view'da dinamik olarak doldurulacak
            'style': 'width: 100%;'
        })
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'Bu kitap hakkında notlarınız...'}),
        label='Notlar'
    )
