"""farmation URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.views.generic import TemplateView

from farm import urls as farm_urls
from hedge import urls as hedge_urls
from optimizer import urls as optimizer_urls
from api import urls as api_urls
from viewer import urls as viewer_urls

urlpatterns = [
    path('igloo/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('tbd/', TemplateView.as_view(template_name="tbd.html"), name='tbd'),
    path('', TemplateView.as_view(template_name="home.html"), name='home'),
    path('help/', TemplateView.as_view(template_name="help.html"),
         name='help'),
    path('farm/', include((farm_urls, 'farm'), namespace='farm')),
    path('hedge/', include((hedge_urls, 'hedge'), namespace='hedge')),
    path('optimizer/',
         include((optimizer_urls, 'optimizer'), namespace='optimizer')),
    path('api-auth/', include('rest_framework.urls')),
    path('api/', include((api_urls, 'api'), namespace='api')),
    path('viewer/', include((viewer_urls, 'viewer'), namespace='viewer')),
]
