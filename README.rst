Crunch.io Dashboard
~~~~~~~~~~~~~~~~~~~

The Crunch.io Dashboard allows users to launch scientific computing clusters in
EC2 with ease.

I will be updating these instructions in the near future as well as publicly
announcing the opensource release of the core dashboard component.


Setup
+++++

Steps for running dash on Ubuntu 10.04::

    mkvirtualenv --no-site-packages crunchio
    git clone git://github.com/godber/crunch.io-dashboard.git dash
    cd dash
    # Install the system dependencies
    sudo apt-get install -y python-dev libgmp3-dev libgmp3c2 build-essential
    # Install the python dependencies
    pip install -r requirements.txt
    # Run the following commands and follow the instructions
    fab setup
    fab bootstrap


Running
+++++++

After you have completed the setup steps you can run the app with the following
command::

    python ./manage.py runserver

And then in another terminal, run the django-task daemon::

    python ./manage.py taskd


Deployment
++++++++++

If you want to deploy this app into production, you can use apache and mod_wsgi
and manage the taskd with supervisor_.  The `scripts/`
directory contains a django.wsgi file and supervisor configuration file to get
you started.


Testing Guidelines
++++++++++++++++++

I am trying to establish which testing frameworks I intend to use for this
application.  At the moment, I have the following two expectations:

  * Use doctests to provide functional usage examples is encouraged.  But it is
    not suitible for general testing.
  * I may make use of django.test TestCases
  * Lettuce tests are the current focus, though that may change.

I have been hoping to use pyccuracy, but I haven't managed to get its basic
example working correctly even.  I have had no response on their mailing list.
I would prefer a BDD style testing framework that actually drives a browser like
pycurracy but lettuce is BDD and runs quickly, so perhaps it is suitable for
some things.

The following two commands can be used to run tests::

    # running the doctests and TestCases
    ./manage.py test cluster
    # running the lettuce tests
    ./manage.py harvest


Attributions
++++++++++++

The dashboard is dependant on a number of open source components and libraries,
most notably StarCluster_.

Austin


.. _StarCluster: http://web.mit.edu/stardev/cluster/
.. _supervisor: http://supervisord.org/  
