import os, sys
sys.path.append('/var/apps')
sys.path.append('/var/apps/dash')

os.environ['DJANGO_SETTINGS_MODULE'] = 'dash.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
