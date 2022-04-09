from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', home, name='home'),
    path('room/<int:pk>/', room, name='room'),
    path('create-room/', CreateRoom.as_view(), name='create-room'),
    path('profile/<str:pk>/', userProfile, name='user-profile'),
    path('registration/', RegisterUser.as_view(), name='registration'),
    path('login/', LoginUser.as_view(), name='login'),
    path('logout/', logout_user, name='logout'),
    path('update-room/<str:pk>/', updateRoom, name='update-room'),
    path('delete-room/<str:pk>/', deleteRoom, name='delete-room'),
    path('delete-message/<str:pk>', deleteMessage, name='delete-message'),
    path('update-user/', updateUser, name='update-user'),
    path('room/<int:id>/action/<str:pk>/', userAction, name='room-action'),
    path('topics/', topicsPage, name='topics'),
    path('activity/', activityPage, name='activity'),
    path('room/<int:id>/participants/', participantsPage, name='participants'),
    path('reset_password/', auth_views.PasswordResetView.as_view(template_name='main/reset_password.html'), name='reset_password'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name='main/reset_password_sent.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='main/reset_password_confirm.html'), name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='main/reset_password_complete.html'), name='password_reset_complete'),
]
