from django.conf.urls import patterns, url
from .views import BundleApi

urlpatterns = patterns('',
                       url(r'bundles/(?P<engine_id>\d*)/?$',
                           BundleApi.as_view(), name='bundles_by_engine'),
                       )
