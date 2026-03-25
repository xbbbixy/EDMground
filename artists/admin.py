from django.contrib import admin
from .models import Artist, Track, Album, AlbumComment
from genres.models import Genre


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'is_rising', 'favorites_count')
    list_editable = ('is_rising',)
    search_fields = ('name',)
    # 必须：让后台显示曲风选择
    filter_horizontal = ('genres',)

@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_artists', 'plays')
    list_filter = ('artists', 'genres')
    search_fields = ('title', 'artists__name')
    filter_horizontal = ('artists', 'genres')  # ✅ 多选 UI

    def get_artists(self, obj):
        return ", ".join(a.name for a in obj.artists.all())
    get_artists.short_description = "艺术家"

@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('artists',)

@admin.register(AlbumComment)
class AlbumCommentAdmin(admin.ModelAdmin):
    list_display = ('album', 'user', 'created_at')
    search_fields = ('content',)
    list_filter = ('created_at',)