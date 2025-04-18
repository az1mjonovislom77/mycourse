import uuid

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ('email', 'phone_number', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Bu email allaqachon mavjud!")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.verification_code = str(uuid.uuid4())
        user.is_active = False
        if commit:
            user.save()
        return user
