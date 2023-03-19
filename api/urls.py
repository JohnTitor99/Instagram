from django.urls import path
from . import views


urlpatterns = [
    path('', views.apiOverview),

    path('user/<str:username>/', views.getUserByName),
    path('user/<int:user_id>/', views.getUserById),
    path('users/', views.getUsers),

    path('posts/<str:username>/', views.getPosts),
    path('add-post/', views.addPost),
    path('update-post/<int:post_id>/', views.updatePost),
    path('delete-post/<int:post_id>/', views.deletePost),

    path('saved-posts/<str:username>/', views.getSavedPosts),

    path('comments/<int:post_id>/', views.getComments),
    path('add-comment/', views.addComment),
    path('update-comment/<int:comment_id>/', views.updateComment),
    path('delete-comment/<int:comment_id>/', views.deleteComment),

    path('followers/<str:username>/', views.getFollowers),
    path('following/<str:username>/', views.getFollowing),
]