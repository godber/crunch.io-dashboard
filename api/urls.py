from django.conf.urls.defaults import *
from piston.resource import Resource
from piston.authentication import HttpBasicAuthentication
from dash.api.handlers import DiskHandler

auth = HttpBasicAuthentication(realm="API Authentication Required")
ad = { 'authentication': auth }

disk_handler = Resource(handler=DiskHandler, **ad)

urlpatterns = patterns('',
   url(r'^disk/(?P<id>[^/]+)/', disk_handler),
)
