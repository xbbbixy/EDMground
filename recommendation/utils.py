import random
from artists.models import Artist,Track


# --------------------------------------------------
# 工具函数：从艺术家列表中抽取歌曲
# --------------------------------------------------
def _collect_tracks_from_artists(artists, limit):
    """
    从给定的 Artist queryset 中，依次抽取其 tracks
    保证：
    - track 有音频
    - 不重复
    """
    tracks = []
    seen_ids = set()

    for artist in artists:
        artist_tracks = (
            artist.tracks
            .exclude(audio_file__isnull=True)
            .exclude(audio_file='')
            .order_by('-plays', '-created_at')
        )

        for t in artist_tracks:
            if t.id in seen_ids:
                continue
            tracks.append(t)
            seen_ids.add(t.id)
            if len(tracks) >= limit:
                return tracks

    return tracks


# --------------------------------------------------
# ① 全站热门歌曲（Artist → Tracks）
# --------------------------------------------------
def get_popular_tracks(limit=10):
    """
    热门推荐逻辑：
    1. 按艺术家热度排序
    2. 从热门艺术家的 tracks 中抽歌
    """
    hot_artists = (
        Artist.objects
        .order_by('-favorites_count')
        .prefetch_related('tracks')
    )

    tracks = _collect_tracks_from_artists(hot_artists, limit)
    random.shuffle(tracks)
    return tracks


# --------------------------------------------------
# ② 个性化推荐（Artist → Tracks）
# --------------------------------------------------
def get_personalized_tracks(user, limit=10):
    """
    个性化推荐策略（清晰可讲）：
    1. 优先：用户收藏的艺术家 → 他们的歌曲
    2. 不足：热门艺术家兜底
    """

    # 未登录，直接走热门
    if not user or not user.is_authenticated:
        return get_popular_tracks(limit)

    tracks = []

    # ---------- ① 收藏艺术家 ----------
    try:
        profile = user.profile
        fav_artists = profile.favorites_artists.all().prefetch_related('tracks')

        if fav_artists.exists():
            tracks = _collect_tracks_from_artists(fav_artists, limit)

        # ---------- ② 不足部分用热门艺术家补 ----------
        if len(tracks) < limit:
            hot_artists = (
                Artist.objects.all()
                .exclude(id__in=[a.id for a in fav_artists])
                .order_by('-favorites_count')
                .prefetch_related('tracks')
            )
            tracks += _collect_tracks_from_artists(
                hot_artists,
                limit - len(tracks)
            )

        random.shuffle(tracks)
        return tracks[:limit]

    except Exception as e:
        print("get_personalized_tracks error:", e)
        return get_popular_tracks(limit)
