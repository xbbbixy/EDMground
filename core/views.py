import random,time
from django.shortcuts import render
from artists.models import Artist
from artists.models import Track as ArtistTrack
from genres.models import Genre
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from events.models import Event
from django.http import JsonResponse
from recommendation.utils import get_popular_tracks, get_personalized_tracks
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.cache import never_cache
from users.models import Playlist

@never_cache
@ensure_csrf_cookie
def home(request):
    if request.GET.get('_ajax') == 'tracks':
        print("🔥🔥🔥 HIT TRACK VIEW 🔥🔥🔥", time.time(), random.random())
        qs = ArtistTrack.objects.filter(audio_file__isnull=False)

        ids = list(qs.values_list('id', flat=True))

        if len(ids) <= 5:
            chosen_ids = ids
        else:
            chosen_ids = random.sample(ids, 5)

        tracks = (
            ArtistTrack.objects
            .filter(id__in=chosen_ids)
            .select_related('artist')
        )

        playlist_track_ids = set()
        if request.user.is_authenticated:
            playlist_track_ids = set(
                Playlist.objects
                .filter(user=request.user)
                .values_list('tracks__id', flat=True)
            )

        payload = []
        for t in tracks:
            payload.append({
                'id': t.id,
                'title': t.title,
                'artist': t.artist.name if t.artist else '',
                'audio': t.audio_file.url if t.audio_file else '',
                'cover': t.cover.url if t.cover else '',
                'is_added': t.id in playlist_track_ids,
            })

        response = JsonResponse({'tracks': payload})

        # 🔥 关键：强制禁用所有缓存
        response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'

        return response

    featured_genres = Genre.objects.filter(is_featured=True)[:6]
    featured_artists = Artist.objects.filter(is_rising=True)[:6]
    featured_events = Event.objects.filter(is_featured=True).order_by('-start_time')[:6]

    if request.user.is_authenticated:
        recommend_tracks = get_personalized_tracks(request.user, limit=5)
    else:
        recommend_tracks = get_popular_tracks(limit=5)

    popular_artists = Artist.objects.all().order_by('-favorites_count')[:5]
    popular_genres = Genre.objects.filter(is_featured=True)[:5]

    playlist_track_ids = set()
    if request.user.is_authenticated:
        playlist_track_ids = set(
            Playlist.objects
            .filter(user=request.user)
            .values_list('tracks__id', flat=True)
        )

    context = {
        'featured_genres': featured_genres,
        'featured_artists': featured_artists,
        'featured_events': featured_events,
        'recommend_tracks': recommend_tracks,
        'popular_artists': popular_artists,
        'popular_genres': popular_genres,
        'playlist_track_ids': playlist_track_ids,
    }
    return render(request, 'core/home.html', context)

def track_list(request):
    query = request.GET.get('q')
    tracks = ArtistTrack.objects.all().order_by('-uploaded_at')

    if query:
        tracks = tracks.filter(title__icontains=query)

    paginator = Paginator(tracks, 8)  # 每页 8 条
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'core/track_list.html', {
        'page_obj': page_obj,
        'query': query,
    })

def track_detail(request, pk):
    track = get_object_or_404(ArtistTrack, pk=pk)
    # 播放次数自增
    track.plays += 1
    track.save()
    return render(request, 'core/track_detail.html', {'track': track})

@require_GET
def random_tracks_by_genre(request):
    slug = request.GET.get("genre", "").strip()
    if not slug:
        return JsonResponse({"tracks": []})

    qs = ArtistTrack.objects.filter(genre_fk__slug=slug).exclude(audio_file="").select_related("artist", "genre_fk")
    tracks = list(qs[:200])  # 防止数据量大时全表 random
    if not tracks:
        return JsonResponse({"tracks": []})

    t = random.choice(tracks)
    audio_url = t.audio_file.url if getattr(t, "audio_file", None) else ""
    return JsonResponse({
        "tracks": [{
            "id": t.id,
            "title": t.title,
            "artist": getattr(t.artist, "name", ""),
            "audio": audio_url,
        }]
    })

