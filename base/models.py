from django.db import models
from django.contrib.auth.models import User

# Create your models here.


# a model to add a logos to users
class UserProfile(models.Model):
    django_user_model = models.OneToOneField(User, on_delete=models.CASCADE, null=False)
    logo = models.ImageField(upload_to='media/logo', null=True, blank=True)


class Comment(models.Model):
    comment_text = models.CharField(max_lenght=200)


# post model
class Post(models.Model):
    logo = models.ImageField(upload_to='media/logo', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    image = models.ImageField(upload_to='media/images', null=True, blank=True)
    post_text = models.TextField(null=True, blank=True)
    likes = models.ManyToManyField(User, related_name="posts")
    comments = models.ManyToManyField(Comment, on_delete=models.DO_NOTHING, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user

    def total_likes(self):
        return self.likes.count()

    class Meta:
        ordering = ['-created']


