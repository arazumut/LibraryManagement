from django import forms
from .models import Book, BookRequest, BookNote

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'isbn', 'library', 'is_available', 'cover_image', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class BookRequestForm(forms.ModelForm):
    class Meta:
        model = BookRequest
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 3, 'placeholder': 'İsteğinizle ilgili bir mesaj bırakabilirsiniz (isteğe bağlı)'}),
        }

class BookRequestResponseForm(forms.ModelForm):
    class Meta:
        model = BookRequest
        fields = ['status', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4, 'placeholder': 'İsteğe yanıtınızı yazın...'}),
        }

class BookNoteForm(forms.ModelForm):
    class Meta:
        model = BookNote
        fields = ['content', 'is_private']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Kitap hakkında notunuzu buraya yazın...'}),
        }
        labels = {
            'is_private': 'Özel not (sadece siz görebilirsiniz)',
        } 