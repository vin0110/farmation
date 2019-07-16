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
from django.contrib import admin, auth
from django.urls import path, include

from django.views.generic import TemplateView

from farm import urls as farm_urls
from optimizer import urls as optimizer_urls
from farm.views import home

urlpatterns = [
    path('igloo/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('tbd/', TemplateView.as_view(template_name="tbd.html"), name='tbd'),
    path('', home, name='home'),
    path('farm/', include((farm_urls, 'farm'), namespace='farm')),
    path('optimizer/',
         include((optimizer_urls, 'farm'), namespace='optimizer')),
]
