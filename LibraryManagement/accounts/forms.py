from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=30, required=False, help_text='İsteğe bağlı')
    last_name = forms.CharField(max_length=30, required=False, help_text='İsteğe bağlı')
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'user_type', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        # SUPER_ADMIN seçeneğini kaldır (sadece admin panelinden oluşturulabilir)
        self.fields['user_type'].choices = [
            (CustomUser.LIBRARY_ADMIN, 'Kütüphane Yöneticisi'),
            (CustomUser.READER, 'Okuyucu'),
        ]

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name'] 