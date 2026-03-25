from django.db import models
from django.conf import settings
from django.urls import reverse
from genres.models import Genre

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True,verbose_name="姓名")
    slug = models.SlugField(unique=True,verbose_name="标签")
    description = models.TextField(blank=True,verbose_name="描述")

    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True,verbose_name="是否显示至主页面")

    class Meta:
        ordering = ['order', 'name']
        verbose_name = "组别"
        verbose_name_plural = "组别"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('community:category', args=[self.slug])


class Post(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='community_posts',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='posts',
        null=True,
        blank=True,
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.SET_NULL,
        related_name='community_posts',
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=200,verbose_name="标题")
    content = models.TextField()

    image = models.ImageField(upload_to='community/images/', blank=True, null=True,verbose_name="图片")
    audio = models.FileField(upload_to='community/audio/', blank=True, null=True,verbose_name="音频文件")
    video = models.FileField(upload_to='community/video/', blank=True, null=True,verbose_name="视频文件")

    likes_count = models.PositiveIntegerField(default=0,verbose_name="点赞数")
    comments_count = models.PositiveIntegerField(default=0,verbose_name="评论数")

    created_at = models.DateTimeField(auto_now_add=True,verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True,verbose_name="更新时间")

    is_pinned = models.BooleanField(default=False, help_text='是否置顶')
    is_featured = models.BooleanField(default=False, help_text='是否社区精选')  # ⭐ 新增
    is_active = models.BooleanField(default=True,verbose_name="是否显示")

    class Meta:
        ordering = ['-is_pinned', '-is_featured', '-created_at']
        verbose_name = "帖子"
        verbose_name_plural = "帖子"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('community:post_detail', args=[self.pk])

class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name="帖子"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='community_comments',
        verbose_name="作者"
    )
    content = models.TextField(verbose_name="内容")

    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='replies',
        verbose_name="隶属"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = "帖子评论"
        verbose_name_plural = "帖子评论"

    def __str__(self):
        return f'Comment by {self.author} on {self.post}'


class PostLike(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name="帖子"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='community_likes',
        verbose_name="用户"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')
        verbose_name = "帖子点赞"

    def __str__(self):
        return f'{self.user} likes {self.post}'


class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='community_notifications',
        verbose_name="用户"
    )
    message = models.CharField(max_length=255,verbose_name="消息")
    link_url = models.CharField(max_length=255, blank=True,verbose_name="链接")  # 点击可跳转到帖子详情
    is_read = models.BooleanField(default=False,verbose_name="已读")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "消息提示"
        verbose_name_plural = "消息提示"

    def __str__(self):
        return f'Notify {self.user}: {self.message[:20]}...'


