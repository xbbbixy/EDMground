from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import RegisterForm, LoginForm
from .models import Playlist
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from artists.models import Artist,Track
from community.models import Post, Notification
from users.decorators import frontend_login_required


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, '注册成功，请登录。')
            return redirect('users:login')
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    # 🔥 关键：只有“普通前端用户”才拦截
    if request.user.is_authenticated and not request.user.is_staff:
        return redirect('core:home')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()

            # 管理员禁止通过前端登录
            if user.is_staff:
                messages.error(request, '管理员账号请从后台登录。')
                return redirect('users:login')

            login(request, user)
            return redirect('core:home')
    else:
        form = LoginForm(request)

    return render(request, 'users/login.html', {'form': form})

def logout_view(request):
    if request.user.is_authenticated and not request.user.is_staff:
        logout(request)
        messages.info(request, '您已安全退出。')
    return redirect('core:home')



@frontend_login_required
def profile_view(request, user_id):
    """
    个人中心：
    - profile_user：当前查看的用户
    - my_posts：TA 在社区发过的帖子（最新 20 条）
    - my_notifications：TA 收到的通知（被点赞 / 被评论）（最新 20 条）
    """
    profile_user = get_object_or_404(User, pk=user_id)

    # 该用户在社区发的帖子
    my_posts = Post.objects.filter(
        author=profile_user
    ).select_related('category').order_by('-created_at')[:20]

    # 通知的基础 QuerySet（不要先切片）
    notif_qs = Notification.objects.filter(
        user=profile_user
    ).order_by('-created_at')

    # 展示列表：只取前 20 条
    my_notifications = notif_qs[:20]

    # 未读数量：在未切片的 notif_qs 上 filter
    unread_count = notif_qs.filter(is_read=False).count()

    playlists = Playlist.objects.filter(user=profile_user)

    context = {
        'profile_user': profile_user,
        'my_posts': my_posts,
        'my_notifications': my_notifications,
        'unread_count': unread_count,
        'playlists': playlists,
    }
    return render(request, 'users/profile.html', context)

@frontend_login_required
def edit_profile(request):
    profile = request.user.profile

    if request.method == 'POST':
        profile.nickname = request.POST.get('nickname')
        profile.bio = request.POST.get('bio')
        profile.instagram = request.POST.get('instagram')
        profile.twitter = request.POST.get('twitter')
        profile.soundcloud = request.POST.get('soundcloud')

        genre_ids = request.POST.getlist('music_genres')
        profile.music_genres.set(genre_ids)

        if request.FILES.get('avatar'):
            profile.avatar = request.FILES['avatar']

        profile.save()
        if profile.nickname:
            request.user.username = profile.nickname
            request.user.save(update_fields=['username'])
        return redirect('users:profile', user_id=request.user.id)

    from genres.models import Genre
    genres = Genre.objects.all()

    return render(request, 'users/edit_profile.html', {
        'profile': profile,
        'genres': genres,
    })


@frontend_login_required
@require_POST
def toggle_favorite_artist(request):
    """
    AJAX toggle 收藏艺术家
    接受 post 参数 artist_id
    返回 JSON: {'status': 'added'/'removed', 'favorites_count': n}
    """
    artist_id = request.POST.get('artist_id')
    if not artist_id:
        return JsonResponse({'error': 'artist_id required'}, status=400)
    try:
        artist = Artist.objects.get(pk=artist_id)
    except Artist.DoesNotExist:
        return JsonResponse({'error': 'artist not found'}, status=404)

    profile = request.user.profile
    if artist in profile.favorites_artists.all():
        profile.favorites_artists.remove(artist)
        # 减少计数但确保不小于 0
        if artist.favorites_count > 0:
            artist.favorites_count -= 1
            artist.save(update_fields=['favorites_count'])
        status = 'removed'
    else:
        profile.favorites_artists.add(artist)
        artist.favorites_count += 1
        artist.save(update_fields=['favorites_count'])
        status = 'added'
    return JsonResponse({'status': status, 'favorites_count': artist.favorites_count})

@frontend_login_required
def notifications_view(request):
    notifications = request.user.community_notifications.all()
    return render(request, 'users/notifications.html', {
        'notifications': notifications
    })

@frontend_login_required
def my_playlists_api(request):
    playlists = Playlist.objects.filter(user=request.user)

    data = {
        'count': playlists.count(),
        'playlists': [
            {
                'id': p.id,
                'name': p.name,
                'cover': p.cover.url if p.cover else '',
            }
            for p in playlists
        ]
    }
    return JsonResponse(data)

@frontend_login_required
@require_POST
def create_playlist_api(request):
    name = request.POST.get('name', '').strip()
    description = request.POST.get('description', '').strip()
    track_id = request.POST.get('track_id')

    if not name:
        return JsonResponse({'error': '歌单名称不能为空'}, status=400)

    playlist = Playlist.objects.create(
        user=request.user,
        name=name,
        description=description
    )

    if request.FILES.get('cover'):
        playlist.cover = request.FILES['cover']
        playlist.save(update_fields=['cover'])

    # 如果创建时带了歌曲
    if track_id:
        track = get_object_or_404(Track, id=track_id)
        playlist.tracks.add(track)

    return JsonResponse({
        'status': 'ok',
        'playlist': {
            'id': playlist.id,
            'name': playlist.name,
            'cover': playlist.cover.url if playlist.cover else '',
        }
    })

@frontend_login_required
@require_POST
def add_track_to_playlists_api(request):
    track_id = request.POST.get('track_id')
    playlist_ids = request.POST.getlist('playlist_ids[]')

    if not track_id or not playlist_ids:
        return JsonResponse({'error': '参数不完整'}, status=400)

    track = get_object_or_404(Track, id=track_id)

    playlists = Playlist.objects.filter(
        id__in=playlist_ids,
        user=request.user  # 🔐 防止越权
    )

    for p in playlists:
        p.tracks.add(track)  # ManyToMany 自动去重

    return JsonResponse({
        'status': 'ok',
        'added_to': playlists.count()
    })

# 删除歌单
@frontend_login_required
@require_POST
def delete_playlist_api(request):
    playlist_id = request.POST.get('playlist_id')
    playlist = get_object_or_404(
        Playlist,
        id=playlist_id,
        user=request.user
    )
    playlist.delete()
    return JsonResponse({'status': 'ok'})

@frontend_login_required
def playlist_detail(request, pk):
    playlist = get_object_or_404(
        Playlist.objects.prefetch_related(
            'tracks__artists',
            'tracks__genres'
        ),
        pk=pk
    )

    return render(request, 'users/playlist_detail.html', {
        'playlist': playlist
    })


@frontend_login_required
@require_POST
def remove_track_from_playlist_api(request):
    playlist_id = request.POST.get('playlist_id')
    track_id = request.POST.get('track_id')

    playlist = get_object_or_404(
        Playlist,
        id=playlist_id,
        user=request.user
    )
    track = get_object_or_404(Track, id=track_id)

    playlist.tracks.remove(track)
    return JsonResponse({'status': 'ok'})


@frontend_login_required
@require_POST
def update_playlist_api(request):
    playlist = get_object_or_404(
        Playlist,
        id=request.POST.get('playlist_id'),
        user=request.user
    )

    playlist.name = request.POST.get('name', playlist.name)
    playlist.description = request.POST.get('description', playlist.description)

    if request.FILES.get('cover'):
        playlist.cover = request.FILES['cover']

    playlist.save()
    return JsonResponse({
        'status': 'ok',
        'playlist': {
            'id': playlist.id,
            'name': playlist.name,
            'description': playlist.description or '',
            'cover': playlist.cover.url if playlist.cover else '',
        }
    })

@frontend_login_required
@require_POST
def remove_track_from_all_playlists_api(request):
    track_id = request.POST.get('track_id')

    if not track_id:
        return JsonResponse({'error': '参数错误'}, status=400)

    playlists = Playlist.objects.filter(
        user=request.user,
        tracks__id=track_id
    )

    for p in playlists:
        p.tracks.remove(track_id)

    return JsonResponse({'status': 'ok'})
