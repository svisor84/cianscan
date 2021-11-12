# -*- coding: utf-8 -*-

from django.conf.urls import include, url
from django.contrib import admin
from django.conf.urls.static import static
from django.shortcuts import HttpResponse
admin.autodiscover()

from . import settings
from django.views.generic import RedirectView

from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView
from office import views

urlpatterns = [
    url(r'^favicon\.ico$', RedirectView.as_view(url='/static/img/favicon.ico'), name='favicon'),
    url(r'^admin_tools/', include('admin_tools.urls')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^login/$', LoginView, {'template_name': 'admin/login.html'}),
    url(r'^logout/$', LogoutView, {'template_name': 'logout.html'}),
    url(r'^password_change/$', PasswordChangeView, {'template_name': 'change_password.html'}),
    url(r'^password_change_done/$', PasswordChangeDoneView, {'template_name': 'password_change_done.html'}, name='password_change_done'),
    url(r'^$', views.home),
    url(r'^feed/$', views.feed),
    url(r'^filters/$', views.filters),
    url(r'^documentation/$', views.documentation),
    url(r'^offers/$', views.offers),
    url(r'^control/$', views.offers_on_control),
    url(r'^notifications/$', views.notifications),
    url(r'^retailers/$', views.retailers),
    url(r'^serp/(?P<filter_id>[\w-]+)/$', views.serp),
    url(r'^offer/(?P<offer_id>[\w-]+)/$', views.offer),
    url(r'^phone_offers/(?P<phone>[\w-]+)/$', views.phone_offers),

    url(r'^ajax/set_offer_moulage/$', views.ajax_set_offer_moulage),
    url(r'^ajax/set_on_control/$', views.ajax_set_on_control),
] + static(settings.SOURCE_STATIC_URL, document_root=settings.SOURCE_STATIC_ROOT) \
  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
  + static('/updates_logs/', document_root=settings.UPDATES_LOGS_ROOT)


if settings.DEBUG:
    urlpatterns += [
        url(r'^robots.txt$',lambda r: HttpResponse("User-agent: *\nDisallow: /", content_type="text/plain")),
    ]
else:
    urlpatterns += [
        url(r'^robots.txt$', lambda r: HttpResponse("", content_type="text/plain")),
    ]
