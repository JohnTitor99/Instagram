from django.db import models
from django.contrib.auth.models import User

# Create your models here.


# a model to add a logos to users
class UserProfile(models.Model):
    django_user_model = models.OneToOneField(User, related_name="users", on_delete=models.CASCADE, null=False)
    logo = models.ImageField(upload_to='media/logo', null=True, blank=True)


# post model
class Post(models.Model):
    logo = models.ImageField(upload_to='media/logo', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    image = models.ImageField(upload_to='media/images', null=True, blank=True)
    post_text = models.TextField(null=True, blank=True)
    likes = models.ManyToManyField(User, related_name="posts")
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.post_text

    def total_likes(self):
        return self.likes.count()

    def users_likes(self):
        return self.likes.all()

    class Meta:
        ordering = ['-created']


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    logo = models.ImageField(upload_to='media/logo', null=True, blank=True)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%s - %s' % (self.post.post_text, self.user)
