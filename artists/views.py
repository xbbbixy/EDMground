from django.shortcuts import render, get_object_or_404,redirect
from django.core.paginator import Paginator
from .models import Artist,Album, Track, AlbumComment
from django.db.models import Q
from genres.models import Genre
from django.urls import reverse
from users.decorators import frontend_login_required
from django.views.decorators.http import require_POST
from django.http import Http404,JsonResponse
from .services import get_hot_tracks, get_hot_albums
from users.models import Playlist


def artist_list(request):
    q = request.GET.get('q', '')
    sort = request.GET.get('sort', 'name')  # name or popularity
    genre_slug = request.GET.get('genre', '')

    artists = Artist.objects.all()

    if q:
        artists = artists.filter(name__icontains=q)

    if genre_slug:
        artists = artists.filter(genres__slug=genre_slug)

    if sort == 'popularity':
        artists = artists.order_by('-favorites_count', '-created_at')
    else:
        artists = artists.order_by('name')

    # 轮播/推荐：选取 is_rising 或 favorites_count Top 6
    carousel_artists = Artist.objects.filter(Q(is_rising=True) | Q(favorites_count__gt=0)).order_by('-favorites_count')[:8]

    paginator = Paginator(artists.distinct(), 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # 所有曲风用于筛选菜单
    genres = Genre.objects.all().order_by('name')

    context = {
        'page_obj': page_obj,
        'carousel_artists': carousel_artists,
        'genres': genres,
        'q': q,
        'sort': sort,
        'selected_genre': genre_slug,
    }
    return render(request, 'artists/list.html', context)


def artist_detail(request, pk):
    artist = get_object_or_404(Artist, pk=pk)
    track_qs = artist.tracks.all().order_by('-plays')
    paginator = Paginator(track_qs, 5)  # 👈 每页 5 条
    page_number = request.GET.get('page', 1)
    tracks_page = paginator.get_page(page_number)
    albums = artist.albums.all().prefetch_related('tracks')
    # 判断当前用户是否已收藏（模板可用）
    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = artist in request.user.profile.favorites_artists.all()

    playlist_track_ids = set()
    if request.user.is_authenticated:
        playlist_track_ids = set(
            Playlist.objects
            .filter(user=request.user)
            .values_list('tracks__id', flat=True)
        )

    context = {
        'artist': artist,
        'tracks_page': tracks_page,
        'albums': albums,
        'is_favorited': is_favorited,
        'playlist_track_ids': playlist_track_ids,
    }
    return render(request, 'artists/detail.html', context)

def album_detail(request, slug):
    album = get_object_or_404(
        Album.objects.prefetch_related(
            'artists',
            'tracks__artists',
            'tracks__genres'
        ),
        slug=slug
    )

    # 一级评论（不包含回复）
    comments = AlbumComment.objects.filter(
        album=album,
        parent__isnull=True
    ).select_related('user').prefetch_related(
        'replies__user',
        'likes'
    )

    playlist_track_ids = set()
    if request.user.is_authenticated:
        playlist_track_ids = set(
            Playlist.objects
            .filter(user=request.user)
            .values_list('tracks__id', flat=True)
        )

    return render(request, 'artists/album_detail.html', {
        'album': album,
        'comments': comments,
        'playlist_track_ids': playlist_track_ids,
    })

@frontend_login_required
def album_comment_create(request, slug):
    if request.method != 'POST':
        raise Http404

    album = get_object_or_404(Album, slug=slug)
    content = request.POST.get('content', '').strip()
    parent_id = request.POST.get('parent_id')

    if not content:
        return redirect(album.get_absolute_url())

    parent = None
    if parent_id:
        try:
            parent = AlbumComment.objects.get(
                id=parent_id,
                album=album
            )
        except AlbumComment.DoesNotExist:
            parent = None  # 防止跨专辑乱回复

    AlbumComment.objects.create(
        album=album,
        user=request.user,
        content=content,
        parent=parent
    )

    return redirect(album.get_absolute_url())

@frontend_login_required
@require_POST
def album_comment_toggle_like(request, comment_id):
    try:
        comment = AlbumComment.objects.get(id=comment_id)
    except AlbumComment.DoesNotExist:
        raise Http404

    user = request.user

    if comment.likes.filter(id=user.id).exists():
        comment.likes.remove(user)
        liked = False
    else:
        comment.likes.add(user)
        liked = True

    return JsonResponse({
        'liked': liked,
        'likes_count': comment.likes.count(),
    })

# 曲库
def library_home(request):
    q = request.GET.get('q', '').strip()
    active_tab = request.GET.get('tab', 'tracks')

    # 热门内容 (侧栏或顶部)
    hot_tracks = Track.objects.filter(is_hot=True).prefetch_related('artists', 'genres').order_by('-plays')[:12]
    hot_albums = get_hot_albums(limit=6)

    # 用户播放列表的歌曲 ID，用于收藏按钮状态
    playlist_track_ids = set()
    if request.user.is_authenticated:
        playlist_track_ids = set(
            Playlist.objects.filter(user=request.user).values_list('tracks__id', flat=True)
        )

    page_obj = None
    if active_tab == 'albums':
        # 查询专辑
        qs = Album.objects.prefetch_related('artists').order_by('-release_date', '-id')
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(artists__name__icontains=q)).distinct()
        paginator = Paginator(qs, 12) # 每页 12 张专辑
        page_obj = paginator.get_page(request.GET.get('page'))
    else:
        # 默认查询歌曲
        qs = Track.objects.select_related('album').prefetch_related('artists', 'genres').order_by('-created_at')
        if q:
            qs = qs.filter(
                Q(title__icontains=q) |
                Q(artists__name__icontains=q) |
                Q(genres__name__icontains=q) |
                Q(album__title__icontains=q)
            ).distinct()
        paginator = Paginator(qs, 20) # 每页 20 首歌曲
        page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'library/home.html', {
        'page_obj': page_obj,
        'hot_tracks': hot_tracks,
        'hot_albums': hot_albums,
        'q': q,
        'playlist_track_ids': playlist_track_ids,
        'active_tab': active_tab,
    })