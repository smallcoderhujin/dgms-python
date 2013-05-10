from django.conf.urls import patterns, include, url
from air_quality.views import *

urlpatterns = patterns('',
    url(r'^list/$',show_list),
    url(r'^export/$',export),
)