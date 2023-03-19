from django.contrib import admin
from .models import Post, UserProfile, Comment, Saved, Follower, Reply, Hashtag

# Register your models here.


admin.site.register(Post),
admin.site.register(UserProfile),
admin.site.register(Comment),
admin.site.register(Saved),
admin.site.register(Follower),
admin.site.register(Reply),
admin.site.register(Hashtag),