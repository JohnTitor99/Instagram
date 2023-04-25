from django.urls import path
from . import views

urlpatterns = [
    path('', views.mainPage, name='main_page'),
    path('register-page/', views.registerPage, name='register_page'),
    path('p/<int:pk>/', views.goToPost, name='go_to_post'),

    path('logout-user/', views.logoutUser, name='logout_user'),
    path('post-action/<int:pk>/', views.postAction, name='post_action'),
    path('delete-post/<int:pk>/', views.deletePost, name='delete_post'),
    path('delete-comment/<int:pk>/', views.deleteComment, name='delete_comment'),
    path('delete-reply/<int:pk>/', views.deleteReply, name='delete_reply'),
]


# x78zum5.xdt5ytf.x1iyjqo2.x182iqb8.xnz67gz