from django.forms import ModelForm, PasswordInput, TextInput
from django.contrib.auth.forms import forms, UserCreationForm

from .models import Post, UserProfile, User


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['image', 'post_text']

        # labels = {
        #     'image': '',
        # }


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['logo', 'gender']
        # excludes = ['']


class RegistrationForm(UserCreationForm):
    username = forms.CharField(widget=TextInput(
        attrs={'type': 'text', 'id': 'username', 'name': 'username', 'class': 'register-page-input', 'placeholder': 'Username'}),
        label=''
    )
    password1 = forms.CharField(widget=PasswordInput(
        attrs={'type': 'text', 'id': 'password', 'name': 'username', 'class': 'register-page-input', 'placeholder': 'Password'}),
        label=''
    )
    password2 = None

