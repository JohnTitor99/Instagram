from django.db import models
from django.contrib.auth.models import User

# Create your models here.


# a model to add a logos to users
class UserProfile(models.Model):
    django_user_model = models.OneToOneField(User, on_delete=models.CASCADE, null=False)
    logo = models.ImageField(upload_to='media/logo', null=True, blank=True)


# post model
class Post(models.Model):
    logo = models.ImageField(upload_to='media/logo', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    image = models.ImageField(upload_to='media/images', null=True, blank=True)
    post_text = models.TextField(null=True, blank=True)
    likes = models.ManyToManyField(User, related_name="posts")
    created = models.DateTimeField(auto_now_add=True)

    def total_likes(self):
        return self.likes.count()

    class Meta:
        ordering = ['-created']