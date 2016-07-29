# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.views.generic.base import RedirectView

from webapp.views import diff

# load admin modules
from django.contrib import admin
admin.autodiscover()


urls = [
    url(r'^$', RedirectView.as_view(pattern_name='admin:index')),
    url(r'^admin/', admin.site.urls),
    url(r'^diff/(?P<content_id>\d+)$', diff),      
]
urlpatterns = urls

# static and media urls not works with DEBUG = True, see static function.
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG_TOOLBAR:
    import debug_toolbar
    urlpatterns.append(url(r'^_x\_debug__/', debug_toolbar.urls))

