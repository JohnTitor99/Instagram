from django.db import models
from django.contrib.auth.models import User

# Create your models here.


# a model to add a logos to users
class UserProfile(models.Model):
    GENDERS = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    logo = models.ImageField(upload_to='media/logo', null=True, blank=True)
    full_name = models.CharField(max_length=50, null=True, blank=True)
    email = models.CharField(max_length=50, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    website = models.CharField(max_length=50, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    gender = models.CharField(max_length=6, null=True, blank=True, choices=GENDERS)

    def __str__(self):
        return self.user.username


# post model
class Post(models.Model):
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


class Saved(models.Model):
    post = models.ForeignKey(Post, related_name="saved",on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="saved", on_delete=models.CASCADE)

    def __str__(self):
        return self.post.post_text

    def is_saved(self):
        return self.user
