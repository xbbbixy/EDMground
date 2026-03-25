from django.urls import path
from . import views

app_name = "recommendation"

urlpatterns = [
    path('', views.recommend_home, name='home'),
    path('like/<int:track_id>/', views.like_track, name='like_track'),
    path('random_tracks_by_genre/', views.random_tracks_by_genre, name='random_tracks_by_genre'),
    path('api/by_genre/', views.api_recommend_by_genre, name='api_by_genre'),
]
