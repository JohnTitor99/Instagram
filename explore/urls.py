from django.urls import path
from . import views

urlpatterns = [
    path('', views.explorePage, name='explore'),
    path('tags/<str:tag>/', views.hashtagPage, name='hashtag_page'),
]