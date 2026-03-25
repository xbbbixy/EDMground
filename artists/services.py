from .models import Track,Album
from django.db.models import Count

def get_hot_tracks(limit=12):
    return (
        Track.objects
        .select_related('album')
        .prefetch_related('artists', 'genres')
        .order_by('-plays', '-created_at')[:limit]
    )

def get_hot_albums(limit=6):
    return (
        Album.objects
        .annotate(comment_count=Count('comments'))
        .order_by('-comment_count', '-created_at')
        .prefetch_related('artists')[:limit]
    )