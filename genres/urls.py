from django.urls import path
from . import views

app_name = 'genres'

urlpatterns = [
    path('', views.genre_list, name='list'),
    path('<slug:slug>/', views.genre_detail, name='detail'),
]
