from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Comment


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text', 'rating']
        widgets = {
            'text': forms.Textarea(attrs={'placeholder': 'Введіть свій коментар'}),
        }


class ReplyForm(forms.Form):
    text = forms.CharField(label='Ваша відповідь', widget=forms.Textarea(attrs={'rows': 1, 'style': 'display:block;', 'placeholder': 'Введіть свою відповідь'}))
