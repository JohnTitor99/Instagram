from django.forms import ModelForm, TextInput
from django.contrib.auth.forms import forms

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['image', 'post_text']

        # labels = {
        #     'image': '',
        # }