from django.urls import path
from . import views

urlpatterns = [
    path('inbox/', views.inboxPage, name='inbox'),
    path('t/<str:chat_user>/', views.openChat, name='open_chat'),
]