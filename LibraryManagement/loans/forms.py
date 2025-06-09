from django import forms
from .models import Loan
from books.models import Book
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model

User = get_user_model()

class LoanForm(forms.ModelForm):
    due_date = forms.DateTimeField(
        label="Son İade Tarihi",
        widget=forms.DateTimeInput(
            attrs={'type': 'datetime-local'},
            format='%Y-%m-%dT%H:%M'
        ),
        required=False,
        help_text="Boş bırakırsanız, bugünden 14 gün sonrası otomatik olarak belirlenecektir."
    )
    
    class Meta:
        model = Loan
        fields = ['book', 'borrower', 'due_date', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Sadece uygun olan kitapları göster
        self.fields['book'].queryset = Book.objects.filter(is_available=True)
        
        # Varsayılan son tarih ayarla (bugünden 14 gün sonra)
        if not self.instance.pk:  # Yeni bir kayıt oluşturuluyorsa
            self.initial['due_date'] = timezone.now() + timedelta(days=14)
            
        # Form alanlarını düzenle
        self.fields['book'].label = "Kitap"
        self.fields['borrower'].label = "Ödünç Alan"
        self.fields['notes'].label = "Notlar"
        
        # Borrower alanını sadece aktif kullanıcılarla sınırla
        self.fields['borrower'].queryset = User.objects.filter(is_active=True) 