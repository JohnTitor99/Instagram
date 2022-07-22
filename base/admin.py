from django.contrib import admin
from .models import Post, UserProfile, Comment, Saved, Like

# Register your models here.


admin.site.register(Post),
admin.site.register(UserProfile),
admin.site.register(Comment),
admin.site.register(Saved),
admin.site.register(Like),