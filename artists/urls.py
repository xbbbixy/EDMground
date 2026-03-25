from django.urls import path
from . import views

urlpatterns = [
    path('', views.artist_list, name='list'),
    path('<int:pk>/', views.artist_detail, name='detail'),
    path('albums/<slug:slug>/', views.album_detail, name='album_detail'),
    # 专辑
    path(
        'albums/<slug:slug>/comment/',
        views.album_comment_create,
        name='album_comment_create'
    ),
    # 专辑评论
    path(
        'albums/comment/<int:comment_id>/like/',
        views.album_comment_toggle_like,
        name='album_comment_toggle_like'
    ),
    # 曲库
    path(
        'library/',
        views.library_home,
        name='library_home'
    ),

]
