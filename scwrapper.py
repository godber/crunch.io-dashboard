#!/usr/bin/env python

import starcluster.config
import starcluster.cluster
import starcluster.volume
import os
import sys
import tempfile
from django.template import Template, Context
from django.conf import settings


class ConfigFile:
    #settings.configure (FOO='bar') # FIXME: Explodes without setting something
    template = Template("""[global]
DEFAULT_TEMPLATE=smallcluster
ENABLE_EXPERIMENTAL=False

[aws info]
AWS_ACCESS_KEY_ID = {{aws_key_id}}
AWS_SECRET_ACCESS_KEY = {{aws_secret_key}}
AWS_USER_ID= {{aws_user_id}}

# Section name should match your key name and be the path to the file.
[key crunch-master]
KEY_LOCATION = {{ssh_key_path}}

[cluster dashcluster]
KEYNAME = crunch-master
CLUSTER_SIZE = {{number_nodes}}
CLUSTER_USER = {{username}}
CLUSTER_SHELL = bash
NODE_IMAGE_ID = {{ami_id}}
NODE_INSTANCE_TYPE = {{node_type}}
AVAILABILITY_ZONE = {{availability_zone}}
{% if home_volume_id %}
VOLUMES = home

# must be available in the AVAILABILITY ZONE above
[volume home]
VOLUME_ID = {{home_volume_id}}
MOUNT_PATH = /home
{% endif %}""")

    def __init__(self, **kwargs):
        """
        ConfigFile requires the following keyword arguments:
        aws_kid
        aws_sec_key
        aws_uid
        ssh_keypath
        number_nodes
        username
        node_type
        ami_id
        home_volume_id (optional)
        """

        # FIXME: Do I need to test if the kwargs match all the vars?
        try:
            self.conf = ConfigFile.template.render(Context(kwargs))
        except:
            print "Error generating the configuration file."
            print "Not all of the variables were filled."
            raise
        self.fd = tempfile.NamedTemporaryFile(delete=False)
        self.fd.write(self.conf)
        self.fd.close()
        self.path = self.fd.name
        self.zone = kwargs['availability_zone']

    def __del__(self):
        os.remove(self.path)


class Cluster:
    def __init__(self, cluster_template, availability_zone):
        """
        self.config is a starcluster.config.StarClusterConfig object
        """

        aws_key_id      = cluster_template.user_profile.awscredential.aws_key_id
        aws_secret_key  = cluster_template.user_profile.awscredential.aws_secret_key
        aws_user_id     = cluster_template.user_profile.awscredential.aws_user_id
        number_nodes    = cluster_template.number_of_nodes
        username        = cluster_template.user_profile.user.username
        node_type       = cluster_template.type_of_nodes.api_name
        architecture    = cluster_template.type_of_nodes.architecture
        #TODO: AMI IDs should be moved into a model of the own
        if architecture == '32':
            ami_id = 'ami-8cf913e5'
        elif architecture == '64':
            ami_id = 'ami-0af31963'
        else:
            raise AttributeError('Invalid Node Type')

        # Generate the Temporary SSH Key File
        temp_fd = tempfile.NamedTemporaryFile(delete=False, suffix='.rsa')
        temp_fd.write(cluster_template.user_profile.awscredential.ssh_key)
        temp_fd.close()
        ssh_key_path = temp_fd.name

        # Get the Home Disk if it exists.
        home_disk       = cluster_template.disk_set.filter(name='Home')[0]
        home_volume_id  = home_disk.home_volume_id

        config_file = ConfigFile(
                aws_key_id        = aws_key_id,
                aws_secret_key    = aws_secret_key,
                aws_user_id       = aws_user_id,
                ssh_key_path      = ssh_key_path,
                number_nodes      = number_nodes,
                username          = username,
                node_type         = node_type,
                ami_id            = ami_id,
                home_volume_id    = home_volume_id,
                availability_zone = availability_zone,
                )

        self.temp_ssh_key_file = ssh_key_path
        self.cluster_name = cluster_template.cluster_tag
        self.config_file  = config_file
        self.config = starcluster.config.StarClusterConfig(self.config_file.path)
        self.config.load()
        self.sc = self.config.get_cluster_template('dashcluster', self.cluster_name)

    def __del__(self):
        os.remove(self.temp_ssh_key_file)

    def launch(self):
        if self.sc.is_valid():
            self.sc.start(create=True)
        else:
            print "Cluster is not valid"

    def terminate(self):
        cfg = self.config
        starcluster.cluster.stop_cluster(self.cluster_name, cfg)

    def createvolume(self, size, zone):
        vc = starcluster.volume.VolumeCreator(self.config)
        volid = vc.create(size, zone)
        if volid:
            print "Your new %sGB volume %s has been created successfully" % \
            (size, volid)
            return volid
        else:
            print "failed to create new volume"


def usage():
    print "You must specify one of the following commands: start, stop createvolume"
    print "Usage:"
    print "        %s (start|stop|createvolume|testconfig)" % sys.argv[0]
    sys.exit(1)


def main():
    import dash.cluster.models as Dash

    if len(sys.argv) != 2:
        usage()

    ct = Dash.ClusterTemplate.objects.get(name="Good Cluster")
    cluster = Cluster(ct, 'us-east-1a')

    command = sys.argv[1]
    if command == 'start':
        cluster.launch()
    elif command == 'stop':
        cluster.terminate()
    elif command == 'createvolume':
        cluster.createvolume(3, 'us-east-1d')
    elif command == 'testconfig':
        print "If you didn't see any exceptions your config didnt explode"
    else:
        usage()

if __name__ == "__main__":
    main()
