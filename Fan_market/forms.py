from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Comment


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Enter your username',
        'class': 'w-full py-4 px-6 rounded-xl'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Your password',
        'class': 'w-full py-4 px-6 rounded-xl'
    }))


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    username = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Enter your username',
        'class': 'w-full py-4 px-6 rounded-xl'
    }))
    email = forms.CharField(widget=forms.EmailInput(attrs={
        'placeholder': 'Your email address',
        'class': 'w-full py-4 px-6 rounded-xl'
    }))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Enter your password',
        'class': 'w-full py-4 px-6 rounded-xl'
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Repeat your password',
        'class': 'w-full py-4 px-6 rounded-xl'
    }))


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text', 'rating']
        widgets = {
            'text': forms.Textarea(attrs={'placeholder': 'Введіть свій коментар'}),
        }


class ReplyForm(forms.Form):
    text = forms.CharField(label='Ваша відповідь', widget=forms.Textarea(attrs={'rows': 1, 'style': 'display:block;'}))
