from fabric.api import *
import glob
import os
from random import choice

def docs():
    print "Generating PDF documentation"
    dir = os.path.dirname(__file__)
    docdir = os.path.join(dir,'docs')
    with cd(docdir):
        local('rst2pdf -o pdf/README.pdf %s/README.rst' % dir)
        for f in glob.glob('%s/*.rst' % docdir):
            filename = os.path.basename(f)
            filehead = os.path.splitext(filename)[0]
            local('rst2pdf -o pdf/%s.pdf %s.rst' % (filehead, filehead))

def bootstrap():
    local('python ./manage.py syncdb --noinput')
    local('python ./manage.py loaddata Ec2InstanceType.json')
    local('python ./manage.py loaddata User.json')
    print 'Change the admin user password:'
    print '  python ./manage.py changepassword admin'

def setup():
    print 'Create and edit the settings_local.py file, some settings are provided below:'
    print '  cp settings_local.py-example settings_local.py'
    print '  vi settings_local.py'
    print "You may use the following key for SECRET_KEY or generate your own:"
    print '  ' + ''.join([choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)])
    print 'You may also want to set STATIC_DOC_ROOT if you are doing development:'
    print '  ' + os.getcwd() + '/cluster/assets'
 
def reset():
    print "Resetting the entire application"
    local('python ./manage.py reset auth --noinput')
    local('python ./manage.py reset cluster --noinput')
    local('python ./manage.py reset djangotasks --noinput')
    bootstrap()

def test():
    print "Run the following commands to run tests:"
    print '  python ./manage.py test cluster'
    print '  python ./manage.py harvest'
