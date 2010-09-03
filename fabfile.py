from fabric.api import *
import glob
import os.path

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
    local('python ./manage.py loaddata UserProfile.json User.json')
    local('python ./manage.py loaddata Ec2InstanceType.json')
 
def reset():
    print "Resetting the entire application"
    local('python ./manage.py reset auth --noinput')
    local('python ./manage.py reset cluster --noinput')
    local('python ./manage.py reset djangotasks --noinput')
    bootstrap()
