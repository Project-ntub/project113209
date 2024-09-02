from django import forms
from .models import CustomUser

class CustomUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'phone', 'email', 'password']  # 添加其他需要的字段
        widgets = {
            'password': forms.PasswordInput(),
        }
