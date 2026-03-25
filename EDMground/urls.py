"""EDMground URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(('core.urls', 'core'), namespace='core')),  # 首页与通用页面
    path('artists/', include(('artists.urls', 'artists'), namespace='artists')),
    path('genres/', include(('genres.urls', 'genres'), namespace='genres')),
    path('events/', include(('events.urls', 'events'), namespace='events')),
    path('recommendation/', include(('recommendation.urls', 'recommendation'), namespace='recommendation')),
    path('accounts/', include(('users.urls', 'users'), namespace='users')),
    path('community/', include(('community.urls', 'community'), namespace='community')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

