from django.urls import path
from .views import *

urlpatterns = [
    path('', getRoute),
    path('rooms/', getRooms),
    path('rooms/<str:pk>/', getRoom),
]