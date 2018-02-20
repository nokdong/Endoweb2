"""endo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,  include
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings

from django.contrib.auth import views as auth_views
#from procedure.views import HomeView, ExamCreateView
from endo.views import UserCreateView, UserCreateDoneTV, HomeView
from procedure import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^accounts/register/$', UserCreateView.as_view(), name='register'),
    url(r'^accounts/register/done/$',UserCreateDoneTV.as_view(), name='register_done'),
    #url(r'^accounts/login', auth_views.login),
    url(r'^$', views.home, name='home'),
    url(r'^procedure/', include('procedure.urls', namespace='procedure'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
