from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text', 'rating']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'placeholder': "Fikringizni yozing..."}),
            'rating': forms.Select(choices=[(i, f"{i} ⭐") for i in range(1, 6)])
        }
