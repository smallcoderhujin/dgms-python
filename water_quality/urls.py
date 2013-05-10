from django.conf.urls import patterns, include, url
from water_quality.views import *

urlpatterns = patterns('',
    url(r'^list/$',water_quality_list),
    url(r'^export/$',export),
)