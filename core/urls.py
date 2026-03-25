from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path('', views.home, name='home'),
    path('tracks/', views.track_list, name='track_list'),
    path('tracks/<int:pk>/', views.track_detail, name='track_detail'),
    path("api/random-by-genre/", views.random_tracks_by_genre, name="random_tracks_by_genre"),
]
