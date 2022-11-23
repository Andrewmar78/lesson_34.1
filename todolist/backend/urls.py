from django.urls import path, include
from django.contrib import admin


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('core/', include('core.urls')),
    path('goals/', include('goals.urls')),
    path('oauth/', include('social_django.urls', namespace='social')),
    path('bot/', include('bot.urls')),
]
