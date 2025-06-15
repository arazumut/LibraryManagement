from django import forms
from .models import Library

class LibraryForm(forms.ModelForm):
    """
    Kütüphane oluşturma ve düzenleme formu
    """
    class Meta:
        model = Library
        fields = ['name', 'description', 'address', 'phone', 'email', 'admins']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Kütüphane adını girin'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Kütüphane hakkında bilgi girin', 'rows': 4}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Kütüphane adresini girin', 'rows': 3}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Telefon numarası girin'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'E-posta adresini girin'}),
            'admins': forms.SelectMultiple(attrs={'class': 'form-select', 'data-control': 'select2', 'data-placeholder': 'Yöneticileri seçin'}),
        }
