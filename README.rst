Crunch.io Dashboard
~~~~~~~~~~~~~~~~~~~

The Crunch.io Dashboard allows users to launch scientific computing clusters in EC2 with ease.

I will be updating these instructions in the near future as well as publically
announcing the opensource release of the core dashboard component.


Setup
+++++

Steps for running dash on Ubuntu 10.04::

    mkvirtualenv --no-site-packages crunchio
    git clone git://github.com/godber/crunch.io-dashboard.git dash
    cd dash
    sudo apt-get install -y python-dev libgmp3-dev libgmp3c2 build-essential
    cp settings_local.py-example settings_local.py
    # Get a random string for SECRET_KEY, this may not be optimal
    python -c 'import os; print os.urandom(50).encode("base64")'
    # Get the STATIC_DOC_ROOT if you're developing
    echo $(pwd)/cluster/assets
    # Set at least the SECRET_KEY in settings_local.py
    vim settings_local.py
    fab bootstrap


Attributions
++++++++++++

The dashboard is dependant on a number of open source components and libraries,
most notably StarCluster_.

Austin


.. _StarCluster: http://web.mit.edu/stardev/cluster/
