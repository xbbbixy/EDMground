from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Genre
from artists.models import Artist, Track
from community.models import Post
from users.models import Playlist

def genre_list(request):
    """
    曲风首页：
    - 主曲风
    - 热门曲风
    - 全部曲风（支持搜索 + 分页）
    """
    query = request.GET.get('q', '').strip()

    # ① 主曲风（一级流派）
    main_genres = Genre.objects.filter(parent__isnull=True).order_by('name')

    # ② 热门曲风（不区分层级，精选展示）
    hot_genres = Genre.objects.filter(is_featured=True).order_by('name')[:8]

    # ③ 全部曲风（你原来的逻辑，基本不动）
    all_genres = Genre.objects.all().order_by('name')

    if query:
        all_genres = all_genres.filter(
            Q(name__icontains=query)
        )

    paginator = Paginator(all_genres, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'main_genres': main_genres,
        'hot_genres': hot_genres,
        'page_obj': page_obj,
        'query': query,
    }
    return render(request, 'genres/list.html', context)

def genre_detail(request, slug):
    """
    曲风详情页：
    - 当前曲风信息
    - 子流派列表
    - 代表作品：按 Track 自己的曲风过滤
    - 相关艺术家：按 Artist 的曲风过滤
    """
    genre = get_object_or_404(Genre, slug=slug)

    # 子流派（如果你在 Genre 里有 parent / subgenres 关系）
    subgenres = genre.subgenres.all()

    # ✅ 代表作品：使用 Track.genres（我们刚刚加的 ManyToMany）
    tracks_qs = Track.objects.filter(
        genres__slug=slug
    ).distinct()

    paginator = Paginator(tracks_qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # ✅ 相关艺术家：仍然用 Artist.genres
    artists = Artist.objects.filter(
        genres__slug=slug
    ).distinct()

    community_posts = Post.objects.filter(
        genre=genre,
        is_active=True
    ).select_related('author', 'category').order_by('-created_at')[:5]

    playlist_track_ids = set()
    if request.user.is_authenticated:
        playlist_track_ids = set(
            Playlist.objects
            .filter(user=request.user)
            .values_list('tracks__id', flat=True)
        )

    context = {
        'genre': genre,
        'subgenres': subgenres,
        'page_obj': page_obj,
        'artists': artists,
        'community_posts': community_posts,
        'playlist_track_ids': playlist_track_ids,
    }
    return render(request, 'genres/detail.html', context)
