from django.contrib import admin
from .models import Category, Post, Comment, PostLike, Notification


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'author',
        'category',
        'is_featured',
        'is_pinned',
        'likes_count',
        'comments_count',
        'created_at',
    )
    list_filter = (
        'category',
        'is_featured',
        'is_pinned',
        'is_active',
    )
    search_fields = ('title', 'content', 'author__username')
    raw_id_fields = ('author',)
    date_hierarchy = 'created_at'



@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'created_at', 'parent')
    search_fields = ('content', 'author__username', 'post__title')
    raw_id_fields = ('post', 'author', 'parent')


@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'created_at')
    raw_id_fields = ('post', 'user')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'link_url', 'is_read', 'created_at')
    list_filter = ('is_read',)
    search_fields = ('message', 'user__username')
    raw_id_fields = ('user',)
