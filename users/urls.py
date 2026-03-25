from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # 认证
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # 个人中心
    path('profile/<int:user_id>/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),

    # 收藏
    path('toggle-favorite-artist/', views.toggle_favorite_artist, name='toggle_favorite_artist'),
    path('api/playlists/', views.my_playlists_api, name='my_playlists_api'),
    path('api/playlists/create/', views.create_playlist_api, name='create_playlist_api'),
    path('api/playlists/add-track/', views.add_track_to_playlists_api, name='add_track_to_playlists_api'),
    path('api/playlists/delete/', views.delete_playlist_api, name='delete_playlist_api'),

    # 歌单详情页
    path('playlists/<int:pk>/', views.playlist_detail, name='playlist_detail'),
    path('api/playlists/remove-track/', views.remove_track_from_playlist_api, name='remove_track_from_playlist_api'),
    path('api/playlists/update/', views.update_playlist_api, name='update_playlist_api'),

    path('api/playlists/remove-track-all/',views.remove_track_from_all_playlists_api,name='remove_track_from_all_playlists_api'),

]
