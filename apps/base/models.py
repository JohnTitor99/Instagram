from django.db import models
from django.contrib.auth.models import User
from io import BytesIO
import sys
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.base import ContentFile

# Create your models here.


# extending a default user model
class UserProfile(models.Model):
    GENDERS = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('', 'Prefer not to say')
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    logo = models.ImageField(upload_to='media/logo', default='media/logo/empty_photo.png')
    full_name = models.CharField(max_length=50, null=True, blank=True)
    email = models.CharField(max_length=50, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    website = models.CharField(max_length=50, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    gender = models.CharField(max_length=17, null=True, blank=True, choices=GENDERS)
    similar_account_suggestions = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        try:
            img = Image.open(self.logo) # get the object of saved logo
            new_image_io = BytesIO()

            image_file_size = len(img.fp.read()) # size of the image in bytes
            width, height = img.size

            # get height and width values for resizing depending on file size
            w = 0
            h = 0
            if image_file_size < 100000:
                w = width
                h = height
            elif 100000 <= image_file_size < 200000:
                w = int(float(width) / 1.1)
                h = int(float(height) / 1.1)
            elif 200000 <= image_file_size < 600000:
                w = int(float(width) / 2.5)
                h = int(float(height) / 2.5)
            elif 600000 <= image_file_size < 4000000:
                w = int(float(width) / 3.5)
                h = int(float(height) / 3.5)
            elif image_file_size >= 4000000:
                w = int(float(width) / 4.5)
                h = int(float(height) /4.5)

            resized  = img.resize((w, h), Image.ANTIALIAS)

            if img.format == 'JPEG' :
                resized.save(new_image_io, format='JPEG')
            elif img.format == 'PNG' :
                resized.save(new_image_io, format='PNG')

            # get the logo name
            temp_name = self.logo.name.split('/')[-1]
            # deleting a current saved logo for saving a new resized image
            self.logo.delete(save=False)

            self.logo.save(
                temp_name,
                content=ContentFile(new_image_io.getvalue()),
                save=False
            )

            super(UserProfile, self).save()
        except:
            pass


class Follower(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="current_user")
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower")
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%s - %s' % (self.user, self.follower)


#! if you need to define an inheritance to model that is below, just add a quotes to inheritance model's name
class Hashtag(models.Model):
    name = models.CharField(max_length=30, null=False, blank=False)

    def __str__(self):
        return self.name


# post model
class Post(models.Model):
    IMAGE_DIMENSIONS = (
        ('1', '1:1'),
        ('2', '4:5'),
        ('3', '16:9')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    image = models.ImageField(upload_to='media/images', null=True, blank=True)
    image_dimensions = models.CharField(max_length=5, choices=IMAGE_DIMENSIONS, default='2')
    post_text = models.TextField(null=True, blank=True)
    likes = models.ManyToManyField(User, related_name="posts", null=True, blank=True)
    hashtag = models.ManyToManyField('Hashtag', related_name="hashtag_posts", null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{user}-{post_text}".format(user=self.user, post_text=self.post_text)

    @property
    def total_likes(self):
        return self.likes.count()

    @property
    def users_likes(self):
        return self.likes.all().values_list('pk', flat=True)

    # changing an image resolution
    def save(self, *args, **kwargs):
        img = Image.open(self.image) # get the object of saved logo
        new_image_io = BytesIO()

        image_file_size = len(img.fp.read()) # size of the image in bytes
        width, height = img.size

        # get height and width values for resizing depending on file size
        w = 0
        h = 0
        if image_file_size < 100000:
            w = width
            h = height
        elif 100000 <= image_file_size < 200000:
            w = int(float(width) / 1.1)
            h = int(float(height) / 1.1)
        elif 200000 <= image_file_size < 600000:
            w = int(float(width) / 2.5)
            h = int(float(height) / 2.5)
        elif 600000 <= image_file_size < 4000000:
            w = int(float(width) / 3.5)
            h = int(float(height) / 3.5)
        elif image_file_size >= 4000000:
            w = int(float(width) / 4.5)
            h = int(float(height) /4.5)

        resized  = img.resize((w, h), Image.ANTIALIAS)

        if img.format == 'JPEG' :
            resized.save(new_image_io, format='JPEG')
        elif img.format == 'PNG' :
            resized.save(new_image_io, format='PNG')

        # get the logo name
        temp_name = self.image.name.replace('media/images/', '')
        # deleting a current saved logo for saving a new resized image
        self.image.delete(save=False)

        self.image.save(
            temp_name,
            content=ContentFile(new_image_io.getvalue()),
            save=False
        )

        super(Post, self).save()

    class Meta:
        ordering = ['-created']


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%s - %s - %s' % (self.post.post_text, self.user, self.body)

    class Meta:
        ordering = ['-created']


class Reply(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="replied_user")
    related_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="related_user", default="")
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.body} / {self.comment.user} - {self.comment.body}"

    class Meta:
        ordering = ['-created']


class Saved(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.post.post_text

    def is_saved(self):
        return self.user