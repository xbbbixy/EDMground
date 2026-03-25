from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from users.decorators import frontend_login_required
from users.models import Playlist
from django.views.decorators.http import require_GET
from genres.models import Genre
from artists.models import Artist,Track
from .models import RecommendationLog
from .utils import get_popular_tracks, get_personalized_tracks
from django.views.decorators.cache import never_cache
import random

@never_cache
def recommend_home(request):
    """
    推荐主页面（整合 AJAX + 首页渲染）
    """

    # ---------- ① AJAX 局部刷新：个性化推荐 tracks ----------
    if request.GET.get('_ajax') == 'tracks':
        if request.GET.get('_ajax') == 'tracks':
            qs = Track.objects.filter(audio_file__isnull=False)

            ids = list(qs.values_list('id', flat=True))
            random.shuffle(ids)
            chosen_ids = ids[:5]

            tracks = Track.objects.filter(id__in=chosen_ids)

            playlist_track_ids = set()
            if request.user.is_authenticated:
                playlist_track_ids = set(
                    Playlist.objects.filter(user=request.user).values_list('tracks__id', flat=True)
                )

            payload = []
            for t in tracks:
                payload.append({
                    'id': t.id,
                    'title': t.title,
                    'audio': t.audio_file.url if t.audio_file else '',
                    'cover': t.cover.url if t.cover else '',
                    'is_added': t.id in playlist_track_ids,
                })

            print("🔥 random tracks =", chosen_ids)
            return JsonResponse({'tracks': payload})

    # ---------- ② AJAX 局部刷新：热门艺术家 ----------
    if request.GET.get('_ajax') == 'artists':
        artists = Artist.objects.all()  # 获取所有艺术家
        artist_ids = list(artists.values_list('id', flat=True))
        random.shuffle(artist_ids)  # 随机打乱
        chosen_artist_ids = artist_ids[:5]  # 选择前 5 个

        # 获取这些随机艺术家
        artists = Artist.objects.filter(id__in=chosen_artist_ids)

        payload = [{
            'id': a.id,
            'name': a.name,
            'favorites_count': a.favorites_count,
            'avatar': a.avatar.url if a.avatar else '',
        } for a in artists]

        return JsonResponse({'artists': payload})

    # ---------- ③ AJAX 局部刷新：热门曲风 ----------
    if request.GET.get('_ajax') == 'genres':
        qs = Genre.objects.all()

        ids = list(qs.values_list('id', flat=True))
        random.shuffle(ids)
        chosen_ids = ids[:5]

        genres = Genre.objects.filter(id__in=chosen_ids)

        payload = []
        for g in genres:
            payload.append({
                'id': g.id,
                'name': g.name,
                'slug': g.slug,
            })

        print("🔥 random genres =", chosen_ids)
        return JsonResponse({'genres': payload})

    # ---------- ③ 正常页面渲染 ----------
    if request.user.is_authenticated:
        personalized = get_personalized_tracks(request.user, limit=8)
        popular = get_popular_tracks(limit=8)
    else:
        personalized = []
        popular = get_popular_tracks(limit=12)

    context = {
        'personalized_tracks': personalized,
        'popular_tracks': popular,
    }
    return render(request, 'recommendation/home.html', context)


# ------------------------------------------------------------
# 随机获取某曲风下的音乐（保留原逻辑）
# ------------------------------------------------------------
@require_GET
def random_tracks_by_genre(request):
    slug = (request.GET.get("genre") or "").strip()
    if not slug:
        return JsonResponse({"tracks": []})

    # ① 找到曲风
    genre = Genre.objects.filter(slug=slug).first()
    if not genre:
        return JsonResponse({"tracks": []})

    # ② 该曲风下的艺术家
    artists = genre.artists.prefetch_related('tracks')

    # ③ 从这些艺术家的 tracks 中筛选可播放的歌
    tracks = []
    for artist in artists:
        artist_tracks = (
            artist.tracks
            .exclude(audio_file__isnull=True)
            .exclude(audio_file='')
        )
        tracks.extend(list(artist_tracks))

    if not tracks:
        return JsonResponse({"tracks": []})

    # ④ 随机取一首
    t = random.choice(tracks)

    return JsonResponse({
        "tracks": [{
            "id": t.id,
            "title": t.title,
            "artist": (
                t.artists.first().name
                if hasattr(t, "artists") and t.artists.exists()
                else ""
            ),
            "audio": t.audio_file.url if t.audio_file else "",
        }]
    })

# ------------------------------------------------------------
# Ajax 点赞接口
# ------------------------------------------------------------
@frontend_login_required
def like_track(request, track_id):
    track = get_object_or_404(Track, pk=track_id)
    track.likes += 1
    track.save()

    RecommendationLog.objects.create(
        user=request.user,
        track=track,
        reason='like'
    )
    return JsonResponse({'likes': track.likes})

@require_GET
def api_recommend_by_genre(request):
  """
  简单推荐：根据曲风 slug 推荐一批歌曲
  GET 参数：
    - genre: 曲风 slug
    - exclude: 可以传多个 exclude=id，用于排除当前播放列表已有的歌曲
  """
  genre_slug = request.GET.get('genre')
  exclude_ids = request.GET.getlist('exclude')

  qs = Track.objects.all()

  if genre_slug:
    qs = qs.filter(genres__slug=genre_slug)

  if exclude_ids:
    qs = qs.exclude(id__in=exclude_ids)

  # 简单策略：按播放量倒序，取前 20
  qs = qs.order_by('-plays')[:20]

  tracks_data = []
  for t in qs:
    # 多艺术家名拼成字符串用于前端展示
    artist_names = " / ".join(a.name for a in t.artists.all())
    genre_slugs = list(t.genres.values_list('slug', flat=True))

    tracks_data.append({
      'id': t.id,
      'title': t.title,
      'artists': artist_names,
      'audio': t.audio_file.url if t.audio_file else '',
      'cover': '',  # 如果以后给 Track 加封面，这里填 url
      'genres': genre_slugs,
    })

  return JsonResponse({'tracks': tracks_data})
