from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from genres.models import Genre
from django.conf import settings

class Artist(models.Model):
    name = models.CharField(max_length=200,verbose_name="姓名")
    country = models.CharField(max_length=100, blank=True,verbose_name="国籍")
    avatar = models.ImageField(upload_to='artists/avatars/', blank=True, null=True,verbose_name="头像")
    bio = models.TextField(blank=True, null=True,verbose_name="简介")

    #  唯一曲风来源
    genres = models.ManyToManyField(Genre, blank=True, related_name='artists',verbose_name="曲风")

    is_rising = models.BooleanField(default=False)

    favorites_count = models.PositiveIntegerField(default=0,verbose_name="收藏")

    twitter = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    facebook = models.URLField(blank=True)
    website = models.URLField(blank=True)

    class Meta:
        verbose_name = "艺术家"
        verbose_name_plural = "艺术家"

    def get_absolute_url(self):
        return reverse('artists:detail', args=[str(self.id)])

    def __str__(self):
        return self.name

class Album(models.Model):

    title = models.CharField(
        max_length=200,
        verbose_name="专辑名"
    )

    slug = models.SlugField(
        max_length=220,
        unique=True,
        blank=True,
        verbose_name="URL 标识"
    )

    artists = models.ManyToManyField(
        'Artist',
        related_name='albums',
        verbose_name="制作人 / 艺术家"
    )

    cover = models.ImageField(
        upload_to='albums/covers/',
        null=True,
        blank=True,
        verbose_name="专辑封面"
    )

    description = models.TextField(
        blank=True,
        verbose_name="专辑简介"
    )

    release_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="发布日期"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ['-release_date', '-created_at']
        verbose_name = "专辑"
        verbose_name_plural = "专辑"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('artists:album_detail', args=[self.slug])


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

class Track(models.Model):
    artists = models.ManyToManyField(
        Artist,
        blank=True,
        related_name='tracks' 
    )
    title = models.CharField(
        max_length=200,
        verbose_name="歌曲名"
    )
    audio_file = models.FileField(
        upload_to='tracks/',
        blank=True,
        null=True,
        verbose_name="音频文件"
    )
    duration = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="时长（秒）"
    )
    plays = models.PositiveIntegerField(
        default=0,
        verbose_name="播放次数"
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    genres = models.ManyToManyField(
        Genre,
        blank=True,
        related_name='artist_tracks',
        related_query_name='artist_track',
        verbose_name="曲风"
    )

    is_hot = models.BooleanField(
        default=False,
        verbose_name="是否为热门歌曲"
    )

    album = models.ForeignKey(
        Album,
        related_name='tracks',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="所属专辑"
    )

    cover = models.ImageField(
        upload_to='tracks/covers/',
        null=True,
        blank=True,
        verbose_name="歌曲封面"
    )

    class Meta:
        ordering = ['-plays']
        verbose_name = "歌曲"
        verbose_name_plural = "歌曲"

    def __str__(self):
        names = ", ".join(a.name for a in self.artists.all()[:3]) or "Unknown"
        return f"{self.title} - {names}"

    def get_album_title(self):
        if self.album:
            return self.album.title
        return self.title

    def get_album(self):
        return self.album

class AlbumComment(models.Model):
    album = models.ForeignKey(
        Album,
        related_name='comments',
        on_delete=models.CASCADE,
        verbose_name="所属专辑"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='album_comments',
        on_delete=models.CASCADE,
        verbose_name="评论用户"
    )

    content = models.TextField(
        verbose_name="评论内容"
    )

    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='replies',
        on_delete=models.CASCADE,
        verbose_name="回复的评论"
    )

    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='liked_album_comments',
        blank=True,
        verbose_name="点赞用户"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="创建时间"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="更新时间"
    )

    class Meta:
        ordering = ['created_at']
        verbose_name = "专辑评论"
        verbose_name_plural = "专辑评论"

    def __str__(self):
        return f"{self.user} on {self.album}: {self.content[:20]}"

    @property
    def likes_count(self):
        return self.likes.count()

    @property
    def is_reply(self):
        return self.parent_id is not None

