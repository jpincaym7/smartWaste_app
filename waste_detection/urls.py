"""
URL configuration for waste_detection project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import include, path
from waste_detection import settings
from django.conf.urls.static import static
from apps.waste.views.home import HomeView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('waste/', include('apps.waste.urls', namespace='waste')),
    path('security/', include('apps.security.urls', namespace='security')),
    path('recycling_points/', include('apps.recycling_points.urls', namespace='recycling_points')),
    path('gamification/', include('apps.gamification.urls', namespace='gamification')),
    path("", HomeView.as_view(), name="home")
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)