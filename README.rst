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
    # Install the system dependencies
    sudo apt-get install -y python-dev libgmp3-dev libgmp3c2 build-essential
    # Install the python dependencies
    pip install -r requirements.txt
    # Run the following commands and follow the instructions
    fab setup
    fab bootstrap


Attributions
++++++++++++

The dashboard is dependant on a number of open source components and libraries,
most notably StarCluster_.

Austin


.. _StarCluster: http://web.mit.edu/stardev/cluster/
