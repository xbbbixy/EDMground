from django.contrib import admin
from .models import Genre

@admin.register(Genre)
class GenreDetailAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_featured')
    search_fields = ('name',)
