from django.contrib.auth.models import User
from django.db import models
from artists.models import Artist,Track
from genres.models import Genre

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile',verbose_name="用户名")
    nickname = models.CharField(max_length=50, blank=True,verbose_name="昵称")
    avatar = models.ImageField(upload_to='users/avatars/', blank=True, null=True,verbose_name="头像")
    bio = models.TextField(blank=True,verbose_name="简述")
    # 社交链接（新增）
    instagram = models.URLField(blank=True,verbose_name="instagram")
    twitter = models.URLField(blank=True,verbose_name="twitter")
    soundcloud = models.URLField(blank=True,verbose_name="soundcloud")

    music_genres = models.ManyToManyField(
        Genre,
        blank=True,
        related_name='users_with_genre',
        verbose_name="喜欢曲风"
    )

    favorites_artists = models.ManyToManyField(Artist, blank=True, related_name='fav_by_users',verbose_name="收藏的艺术家")

    class Meta:
        verbose_name = "用户页"
        verbose_name_plural = "用户页"

    def __str__(self):
        return self.user.username

class Playlist(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='playlists',
        verbose_name='所属用户'
    )
    name = models.CharField(max_length=100, verbose_name='歌单名称')
    description = models.TextField(blank=True, verbose_name='歌单简介')
    cover = models.ImageField(
        upload_to='users/playlists/',
        blank=True,
        null=True,
        verbose_name='歌单封面'
    )
    tracks = models.ManyToManyField(
        Track,
        related_name='in_playlists',
        blank=True,
        verbose_name='歌曲'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = '歌单'
        verbose_name_plural = '歌单'

    def __str__(self):
        return f'{self.name} ({self.user.username})'

