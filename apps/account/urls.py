from django.urls import path
from . import views

urlpatterns = [
    path('edit/', views.accountsEdit, name="accounts_edit"),
    path('password-change/', views.accountsPasswordChange, name='accounts_password_change'),
    path('<str:user>/saved/', views.userProfileSaved, name='user_profile_saved'),
    path('<str:user>/', views.userProfile, name='user_profile'),

    path('remove-logo', views.removeLogo, name='remove_logo'),
]