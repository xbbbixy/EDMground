from django.shortcuts import render, get_object_or_404, redirect
from users.decorators import frontend_login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.db.models import Count, Q
from genres.models import Genre
from .models import Category, Post, Comment, PostLike, Notification
from django.views.decorators.http import require_POST


def community_home(request):
    """
    社区首页：
    - 精选帖子（主内容）
    - 板块导航（侧栏）
    - 热门帖子（侧栏）
    """
    categories = Category.objects.filter(is_active=True).order_by('order')

    # ⭐ 社区精选帖子（人工运营）
    featured_posts = Post.objects.filter(
        is_active=True,
        is_featured=True
    ).select_related('author', 'category').order_by('-created_at')[:10]

    # 热门帖子（点赞 + 评论）
    hot_posts = Post.objects.filter(
        Q(likes_count__gte=5) | Q(comments_count__gte=5),
        is_active=True
    ).annotate(
        hot_score=Count('likes') + Count('comments')
    ).order_by('-hot_score', '-created_at')[:10]

    # 所有帖子（分页）
    all_posts_qs = Post.objects.filter(is_active=True).select_related('author', 'category').order_by('-created_at')
    paginator = Paginator(all_posts_qs, 5)  # 每页 5 篇
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'community/home.html', {
        'categories': categories,
        'featured_posts': featured_posts,
        'hot_posts': hot_posts,
        'page_obj': page_obj,
    })


def category_posts(request, slug):
    """
    某个板块下的帖子列表
    """
    category = get_object_or_404(Category, slug=slug, is_active=True)
    posts_qs = category.posts.filter(is_active=True).select_related('author', 'category')

    q = request.GET.get('q', '')
    if q:
        posts_qs = posts_qs.filter(title__icontains=q)

    paginator = Paginator(posts_qs, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'community/category.html', {
        'category': category,
        'page_obj': page_obj,
        'q': q,
    })


def post_detail(request, pk):
    """
    帖子详情 + 评论列表
    """
    post = get_object_or_404(
        Post.objects.select_related('author__profile', 'category', 'genre'),
        pk=pk, 
        is_active=True
    )
    comments_qs = post.comments.select_related('author', 'author__profile').order_by('created_at')
    
    # 构建评论树
    comment_map = {c.id: c for c in comments_qs}
    comments_tree = []
    for comment in comments_qs:
        if comment.parent_id:
            parent = comment_map.get(comment.parent_id)
            if parent:
                if not hasattr(parent, 'children'):
                    parent.children = []
                parent.children.append(comment)
        else:
            comments_tree.append(comment)

    is_liked = False
    if request.user.is_authenticated:
        is_liked = PostLike.objects.filter(post=post, user=request.user).exists()

    return render(request, 'community/detail.html', {
        'post': post,
        'comments': comments_tree,
        'is_liked': is_liked,
    })


@frontend_login_required
def post_create(request):
    """
    发表新帖（支持图片 / 音频 / 视频 / 关联曲风）
    """
    categories = Category.objects.filter(is_active=True).order_by('order')
    genres = Genre.objects.all().order_by('name')

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        category_id = request.POST.get('category')
        genre_id = request.POST.get('genre')  # 可选

        if not title or not content or not category_id:
            return render(request, 'community/post_form.html', {
                'categories': categories,
                'genres': genres,
                'error': '标题、内容和板块不能为空。',
            })

        category = get_object_or_404(Category, id=category_id, is_active=True)

        post = Post.objects.create(
            author=request.user,
            category=category,
            title=title,
            content=content,
        )

        # 关联曲风（可选）
        if genre_id:
            try:
                g = Genre.objects.get(pk=genre_id)
                post.genre = g
            except Genre.DoesNotExist:
                pass

        # 上传的附件（如果你前面已经加过 image/audio/video，这里继续保留）
        image = request.FILES.get('image')
        audio = request.FILES.get('audio')
        video = request.FILES.get('video')

        if image:
            post.image = image
        if audio:
            post.audio = audio
        if video:
            post.video = video

        # 如果有任何修改就保存
        post.save()

        return redirect(post.get_absolute_url())

    # GET 请求，默认如果通过 ?category=ID 或 ?genre=ID，可以预选
    selected_category = request.GET.get('category')
    selected_genre = request.GET.get('genre')

    return render(request, 'community/post_form.html', {
        'categories': categories,
        'genres': genres,
        'selected_category': selected_category,
        'selected_genre': selected_genre,
    })

@frontend_login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk, is_active=True)

    if request.method != 'POST':
        return HttpResponseBadRequest('Invalid method')

    content = request.POST.get('content', '').strip()
    if not content:
        return JsonResponse({'error': 'empty'}, status=400)

    parent_id = request.POST.get('parent_id')
    parent_comment = None
    if parent_id:
        try:
            # 确保父评论属于当前帖子
            parent_comment = Comment.objects.get(id=parent_id, post=post)
        except Comment.DoesNotExist:
            return JsonResponse({'error': 'Parent comment not found'}, status=400)

    comment = Comment.objects.create(
        post=post,
        author=request.user,
        content=content,
        parent=parent_comment
    )

    # 更新评论数
    post.comments_count = post.comments.count()
    post.save(update_fields=['comments_count'])
    
    # 如果是回复，通知被回复的人; 否则通知楼主
    if parent_comment and request.user != parent_comment.author:
        Notification.objects.create(
            user=parent_comment.author,
            message=f'{request.user.username} 回复了你的评论',
            link_url=post.get_absolute_url() + f'#comment-{comment.id}',
        )
    elif not parent_comment and request.user != post.author:
        Notification.objects.create(
            user=post.author,
            message=f'你的帖子《{post.title}》收到了来自 {request.user.username} 的评论',
            link_url=post.get_absolute_url(),
        )


    # Ajax 请求 → 返回 JSON
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'id': comment.id,
            'author': {
                'id': comment.author.id,
                'username': comment.author.username,
                'avatar_url': comment.author.profile.avatar.url if comment.author.profile.avatar else ''
            },
            'content': comment.content,
            'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M'),
            'parent_id': parent_id,
        })

    # 非 Ajax 兜底
    return redirect(post.get_absolute_url())


@frontend_login_required
@require_POST
def toggle_like(request, pk):
    post = get_object_or_404(Post, pk=pk, is_active=True)

    # 先查
    like = PostLike.objects.filter(post=post, user=request.user).first()

    if like:
        # 已点赞 -> 取消
        like.delete()
        liked = False
    else:
        # 未点赞 -> 新建
        try:
            PostLike.objects.create(post=post, user=request.user)
            liked = True
            if request.user != post.author:
                Notification.objects.create(
                    user=post.author,
                    message=f'你的帖子《{post.title}》收到了来自{request.user.username}的点赞',
                    link_url=post.get_absolute_url(),
                )
        except IntegrityError:
            # 极端并发兜底：如果刚好被别的请求建了
            liked = True

    # 统一以数据库为准
    post.likes_count = PostLike.objects.filter(post=post).count()
    post.save(update_fields=['likes_count'])

    return JsonResponse({
        'liked': liked,
        'likes_count': post.likes_count,
    })

@frontend_login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    post.delete()
    return redirect("profiles:my_posts")