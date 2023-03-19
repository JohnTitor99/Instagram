from django.db import models
from django.contrib.auth.models import User
from base.models import Post, UserProfile, Comment, Saved


class Chat(models.Model):
    text = models.CharField(max_length=500)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_user')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_user2')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text
