from django.urls import path
from . import views

app_name = 'community'

urlpatterns = [
    path('', views.community_home, name='home'),
    path('category/<slug:slug>/', views.category_posts, name='category'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/new/', views.post_create, name='post_create'),
    path('post/<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('post/<int:pk>/like/', views.toggle_like, name='toggle_like'),
    path('post/delete/<int:post_id>/', views.delete_post, name='delete_post')
]
