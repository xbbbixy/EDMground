from django.contrib import admin
from django.utils.html import format_html
from .models import Event
from genres.models import Genre

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    # 在列表页显示的列
    list_display = ('title', 'city', 'start_time', 'is_featured', 'genre_list', 'poster_preview')
    # 可点击进入编辑的列
    list_display_links = ('title',)
    # 可编辑（在列表页内直接修改）的字段
    list_editable = ('is_featured',)
    # 可用于过滤的字段（侧栏）
    list_filter = ('city', 'is_featured', 'genres')
    # 可用于搜索的字段
    search_fields = ('title', 'organizer', 'city')
    # M2M 字段在编辑页使用水平选择框（用户体验更好）
    filter_horizontal = ('genres',)
    # 如果 Event 模型中有很多字段，需要排版时可以使用 fieldsets
    fieldsets = (
        (None, {
            'fields': ('title', 'organizer', 'city', 'venue', 'start_time', 'end_time', 'is_featured')
        }),
        ('媒体与票务', {
            'fields': ('poster', 'price', 'purchase_info', 'ticket_link')
        }),
        ('关联', {
            'fields': ('genres',)
        }),
        ('内容', {
            'fields': ('description',)
        }),
    )

    readonly_fields = ('poster_preview',)  # poster_preview 在详情页只读显示

    def genre_list(self, obj):
        """在列表页显示该事件关联的曲风名（逗号分隔）"""
        return ", ".join([g.name for g in obj.genres.all()])
    genre_list.short_description = '曲风'

    def poster_preview(self, obj):
        """在 admin 列表/详情显示海报缩略图（如果存在）"""
        if obj.poster:
            return format_html('<img src="{}" style="width:96px; height:auto; object-fit:cover; border-radius:4px;" />', obj.poster.url)
        return "-"
    poster_preview.short_description = '海报预览'
