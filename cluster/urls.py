from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('dash.cluster.views',
    (r'^$', 'dash'),
    (r'^create/$', 'create'),
    (r'^(?P<cluster_template_id>\d+)/launch$', 'launch'),
    (r'^(?P<cluster_template_id>\d+)/history$', 'history'),
    (r'^(?P<cluster_instance_id>\d+)/terminate$', 'terminate'),
    (r'^account/(?P<user_id>\d+)/$', 'account'),
    (r'^account/create/$', 'account_create'),
    (r'^account/ssh_key$', 'ssh_key'),
    (r'^register/$', 'register'),
)

urlpatterns += patterns('',
    (r'^account/password$', 'django.contrib.auth.views.password_change',
        {
            'template_name': 'registration/password_change.html',
            'post_change_redirect': '/',
        }
        ),
    )

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^js/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.STATIC_DOC_ROOT + '/js/' }),
        (r'^css/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.STATIC_DOC_ROOT + '/css/' }),
        (r'^img/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.STATIC_DOC_ROOT + '/img/' }),
        (r'^movie/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.STATIC_DOC_ROOT + '/movie/' }),
    )

