from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Event
from genres.models import Genre
from django.db.models import Q

def event_list(request):
    q = request.GET.get('q', '')
    city = request.GET.get('city', '')
    genre_slug = request.GET.get('genre', '')
    date_order = request.GET.get('date', 'upcoming')  # upcoming or past

    events = Event.objects.all()

    if q:
        events = events.filter(title__icontains=q)
    if city:
        events = events.filter(city__icontains=city)
    if genre_slug:
        events = events.filter(genres__slug=genre_slug)

    if date_order == 'upcoming':
        events = events.order_by('start_time')
    elif date_order == 'recent':
        events = events.order_by('-start_time')

    # 热门活动： is_featured 或按时间接近的活动
    carousel_events = Event.objects.filter(is_featured=True).order_by('-start_time')[:6]

    paginator = Paginator(events.distinct(), 9)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)

    genres = Genre.objects.filter(parent__isnull=True)

    context = {
        'page_obj': page_obj,
        'carousel_events': carousel_events,
        'genres': genres,
        'q': q,
        'city': city,
        'genre_slug': genre_slug,
    }
    return render(request, 'events/list.html', context)


def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    return render(request, 'events/detail.html', {'event': event})