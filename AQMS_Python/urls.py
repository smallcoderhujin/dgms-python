from django.conf.urls import patterns, include, url
from AQMS_Python.views import *

urlpatterns = patterns('',
    url(r'^$',get_login),
    url(r'^home/$',home),
    url(r'^login/$',login),
    url(r'^start/$',start),
    url(r'^air_quality/',include('air_quality.urls')),
    url(r'^water_quality/',include('water_quality.urls')),
)
