from django.forms import ModelForm, PasswordInput, TextInput
from django.contrib.auth.forms import forms, UserCreationForm

from .models import Post, UserProfile, User


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['image_dimensions']


# class UserProfileForm(forms.ModelForm):
#     class Meta:
#         model = UserProfile
#         fields = ['logo']


class RegistrationForm(UserCreationForm):
    username = forms.CharField(widget=TextInput(
        attrs={'id': 'username', 'placeholder': 'Username', 'aria-label': 'Username', 'maxlength': '30', 'type': 'text', 'class': 'register-page-field _aa4b _add6 _ac4d'}),
        label=''
    )
    password1 = forms.CharField(widget=PasswordInput(
        attrs={'id': 'password', 'placeholder': 'Password', 'aria-label': 'Password', 'type': 'password', 'class': 'register-page-field _aa4b _add6 _ac4d'}),
        label=''
    )
    password2 = None

