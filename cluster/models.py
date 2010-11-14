from django.db import models
from django.db.models.signals import post_save  
from django.contrib.auth.models import User
from djangotasks.models import register_task
from django_fields.fields import EncryptedTextField, EncryptedCharField

from django.conf import settings

import datetime
import os, sys

class Ec2InstanceType(models.Model):
    """
    name                - The descriptive name of the instance
    api_name            - The AWS API name (m1.media
    memory              - Memory Allocated to Instance in GB
    compute_units       - Number of EC2 Compute Units
    compute_description - Description of Compute Units
    instance_storage    - Total storage attached to Instance in GB
    storage_description - Description of Storage
    io_performance      - As specified by Amazon: Moderate or High
    architecture        - 
    hourly_price        - the price per node per hour, in dollars, of the corresponding
                          EC2 on-demand instance.  Right now this is us-east-1 pricing.
    """
    ARCHITECTURE_CHOICES = (
        ( '32', '32-bit' ),
        ( '64', '64-bit' )
    )
    IO_PERFORMANCE_CHOICES = (
        ( 'moderate', 'Moderate'),
        ( 'high', 'High'),
    )
    name                = models.CharField(max_length = 100)
    api_name            = models.CharField(max_length = 100)
    memory              = models.FloatField()
    compute_units       = models.FloatField()
    compute_description = models.CharField(max_length = 255)
    instance_storage    = models.IntegerField()
    storage_description = models.CharField(max_length = 255)
    io_performance      = models.CharField(max_length = 20, choices = IO_PERFORMANCE_CHOICES)
    architecture        = models.CharField(max_length = 10, choices = ARCHITECTURE_CHOICES)
    # TODO: hourly_price might need to be pushed out into its own model
    hourly_price        = models.DecimalField(max_digits = 5, decimal_places = 3)

    def __unicode__(self):
        return self.name + ' (' + str(self.api_name) + ')'


class UserProfile(models.Model):
    """
    A UserProfile represents a Crunch.io Account, it might be possible down the
    line for a user to have multiple accounts.  Actually, I am unsure of this,
    the UserProfile used to be where I stored attributes about the account but
    most of those were AWS related and have been pushed into the AwsCredential
    model at this point.

    >>> user = User( username = 'testusername', email = 'test@crunch.io' )
    >>> user.set_password('testpassword')
    >>> user.is_active = False
    >>> user.save()
    >>> user_profile = UserProfile( user = user, credit = '0.00', next_user_clustertemplate_id = 1 )
    >>> user_profile.save()
    """
    class Admin: pass

    user           = models.ForeignKey(User, unique=True)
    credit         = models.DecimalField(max_digits = 8, decimal_places = 2)
    next_user_clustertemplate_id = models.IntegerField()

    def __str__(self):
        return "%s's profile" % self.user  


class AwsCredential(models.Model):
    user_profile   = models.OneToOneField('UserProfile')
    aws_user_id    = models.CharField(max_length = 200)
    aws_email      = models.EmailField(blank=True, null=True)
    ssh_key        = EncryptedTextField()
    aws_key_id     = EncryptedCharField(max_length = 200)
    aws_secret_key = EncryptedCharField(max_length = 200)

    def __unicode__(self):
        return self.aws_user_id + ' (' + str(self.aws_email) + ')'


class ClusterTemplate(models.Model):
    """
    A ClusterTemplate is the template or definition of a cluster that can be
    launched.  These will be saved and shown to users unless they are deleted or
    archived.

    user_clustertemplate_id - Unique per user cluster template identifier
    """

    STATUS_CHOICES = (
        ('disk-creating', 'Disk is being created'),
        ('stopped', 'Stopped'),
        ('stopping', 'Shutting down'),
        ('starting', 'Starting'),
        ('running', 'Running'),
    )

    user_profile       = models.ForeignKey(UserProfile)
    name               = models.CharField(max_length=100)
    number_of_nodes    = models.IntegerField()
    type_of_nodes      = models.ForeignKey('Ec2InstanceType')
    creation_time      = models.DateTimeField()
    is_demo            = models.BooleanField()
    status             = models.CharField(max_length = 20, choices = STATUS_CHOICES)
    user_clustertemplate_id = models.IntegerField()

    def __unicode__(self):
        return self.name + ' (' + str(self.user_profile) + ')'

    def _get_cluster_tag(self):
        """
        Returns the StarCluster compatible cluster tag from creationg time

        This cluster_tag is used in place of the human readable name, it is
        utilized by the underlying StarCluster library and will appear in the
        security groups automatically created while launching a cluster.  It
        serves as a unique identifier.
        """
        return self.creation_time.strftime("%Y%m%d%H%M%S")
    cluster_tag = property(_get_cluster_tag)

class ClusterInstance(models.Model):
    """
    A ClusterInstance represents a running cluster and is derived from a
    ClusterTemplate
    """
    cluster_template  = models.ForeignKey('ClusterTemplate')
    launch_time       = models.DateTimeField()
    termination_time  = models.DateTimeField(blank=True, null=True)
    availability_zone = models.CharField(max_length=50, blank=True, null=True)

    def __unicode__(self):
        return str(self.launch_time)

    def is_running(self):
        return not bool(self.termination_time)

    def launch(self,msg=''):
        """
        In order to launch a ClusterInstance the following requirements must be
        satisfied:
            * A snapshot of the home volume must exist and be shared with the
              launching user (this should have been created at the
              ClusterTemplate creation time)
            * The user has AWS credentials including an ssh keypair.
            * A valid ClusterTemplate has been created.
        """
        from boto.ec2.connection import EC2Connection
        import scwrapper
        import random
        import time
        import datetime
        # FIXME: Add timestamps to logs.

        # Assigning Cluster Parameters
        aws_key_id     = self.cluster_template.user_profile.awscredential.aws_key_id
        aws_secret_key = self.cluster_template.user_profile.awscredential.aws_secret_key
        is_demo        = self.cluster_template.is_demo

        if ( not aws_key_id ) or ( not aws_secret_key ):
            raise 'AwsCredentialError'

        # Randomly selecting a us-east-1{a,b,c,d} availability zone
        # Maybe someday Amazon will give us capacity ideas
        availability_zone = 'us-east-1' + random.choice(('a','b','c','d'))

        # The availability zone needs to be saved for later actions on this
        # ClusterInstance
        self.availability_zone = availability_zone
        self.save()

        # Get latest_snapshot_id
        # TODO: When we support multiple disks, do this for all snapshots
        home_disk = self.cluster_template.disk_set.filter(name='Home')[0]
        latest_snapshot_id = home_disk.latest_snapshot_id
        size = int(home_disk.size)

        if is_demo:
            time.sleep(10)
            home_disk.home_volume_id = 'vol-aaaa1111'
            home_disk.save()
            self.cluster_template.status = 'running'
            self.cluster_template.save()
            print "DEMO: Launching cluster %s in availability zone %s" % \
                    ('demo-cluster', self.availability_zone)
            sys.stdout.flush()
        else:
            # create volume from snapshot in availability_zone
            print "Creating EBS volume from snapshot: %s" % latest_snapshot_id
            sys.stdout.flush()
            conn = EC2Connection(str(aws_key_id), str(aws_secret_key))
            volume = conn.create_volume( size, availability_zone, latest_snapshot_id)
            home_volume_id = volume.id

            # The home_volume_id needs to be saved for later.
            home_disk.home_volume_id = home_volume_id
            home_disk.save()

            star_cluster = scwrapper.Cluster(
                    self.cluster_template,
                    self.availability_zone,
                    )
            print "Launching cluster %s in availability zone %s" % \
                    (star_cluster.cluster_name, self.availability_zone)
            sys.stdout.flush()
            star_cluster.launch()
            sys.stdout.flush()
            self.cluster_template.status = 'running'
            self.cluster_template.save()

            print "Cluster started, saving nodes"
            sys.stdout.flush()
            
            # A new object must be created to get the updated node information.
            running_cluster = scwrapper.Cluster(
                    self.cluster_template,
                    self.availability_zone,
                    )

            # Create the Ec2Instance (Node) objects
            for node in running_cluster.sc.nodes:
                print "Saving node: %s, %s, %s" % ( 
                        node.alias,
                        node.ip_address,
                        node.id
                        )
                sys.stdout.flush()
                instance = Ec2Instance(
                    cluster_instance = self,
                    instance_type    = Ec2InstanceType.objects.filter(api_name = node.instance_type)[0],
                    alias            = node.alias,
                    arch             = node.arch,
                    instance_id      = node.id,
                    image_id         = node.image_id,
                    launch_time = datetime.datetime.strptime(
                        node.launch_time,
                        "%Y-%m-%dT%H:%M:%S.000Z"
                        ),
                    placement          = node.placement,
                    ip_address         = node.ip_address,
                    dns_name           = node.dns_name,
                    private_ip_address = node.private_ip_address,
                    public_dns_name    = node.public_dns_name,
                    state              = node.state
                )
                instance.save()
                print "Saved node: %s" % node.alias
                sys.stdout.flush()

            print "Launching of cluster completed."
            sys.stdout.flush()
 
        return "finished"

    def terminate(self,msg=''):
        from boto.ec2.connection import EC2Connection
        import scwrapper
        import ec2utils
        import time
        aws_key_id     = str(self.cluster_template.user_profile.awscredential.aws_key_id)
        aws_secret_key = str(self.cluster_template.user_profile.awscredential.aws_secret_key)
        is_demo        = self.cluster_template.is_demo

        home_disk = self.cluster_template.disk_set.filter(name='Home')[0]
        home_volume_id = home_disk.home_volume_id

        if is_demo:
            time.sleep(10)
            print "DEMO: Terminating cluster %s in %s availability zone." % \
                    ('demo-cluster', self.availability_zone)
            home_disk.latest_snapshot_id = 'snap-aaaa1112'
            home_disk.home_volume_id = ''
            home_disk.save()
            self.cluster_template.status = 'stopped'
            self.cluster_template.save()
        else:
            star_cluster = scwrapper.Cluster(
                    self.cluster_template,
                    self.availability_zone,
                    )
            print "Terminating cluster %s in %s availability zone." % \
                    (star_cluster.cluster_name, self.availability_zone)
            sys.stdout.flush()
            star_cluster.terminate()
            sys.stdout.flush()

            ec2utils.wait_for_volume_state(
                    aws_key_id,
                    aws_secret_key,
                    home_volume_id,
                    'available',
                    )

            print "Creating snapshot from EBS volume: %s" % home_volume_id
            sys.stdout.flush()
            conn = EC2Connection(aws_key_id, aws_secret_key)
            snapshot = conn.create_snapshot(
                    home_volume_id,
                    "Snapshot for cluster: %s" % star_cluster.cluster_name
                    )
            # FIXME: I am not quite sure how to test if the snapshot really worked
            #        it is critical to ensure that the volume is not deleted if
            #        the snapshot does not succeed.
            if snapshot:
                home_disk.latest_snapshot_id = snapshot.id
                print "Snapshot created: %s" % snapshot.id
                home_disk.home_volume_id = ''
                home_disk.save()
                conn.delete_volume(home_volume_id)
                print "Volume deleted: %s" % home_volume_id
                sys.stdout.flush()
            else:
                print "ERROR: Failed to create snapshot of volume %s" % \
                        home_volume_id
                # TODO: Add email notification
            self.cluster_template.status = 'stopped'
            self.cluster_template.save()
            print "Termination completed"
            sys.stdout.flush()

        return "finished"


class Disk(models.Model):
    """
    This represents a disk that gets attached to a cluster.  There may be both
    EBS Volumes and Snapshots which represent versions of this disk.
    """
    cluster_template   = models.ForeignKey('ClusterTemplate')
    size               = models.IntegerField()
    name               = models.CharField(max_length = 100, default = 'Home')
    mount_path         = models.CharField(max_length = 100, default = '/home')
    partition          = models.IntegerField(default = 1)
    latest_snapshot_id = models.CharField(max_length = 20, blank = True, null = True)
    home_volume_id     = models.CharField(max_length = 20, blank = True, null = True)

    def __unicode__(self):
        return "%f GB disk for %s" % (self.size, self.cluster_template)

    def make_initial_snapshot(self, msg=''):
        from boto.ec2.connection import EC2Connection
        import scwrapper
        import random
        import time

        aws_key_id     = str(self.cluster_template.user_profile.awscredential.aws_key_id)
        aws_secret_key = str(self.cluster_template.user_profile.awscredential.aws_secret_key)
        is_demo        = self.cluster_template.is_demo

        # The availablility zone is randomly chosen since we are just generating
        # a snapshot.
        availability_zone = 'us-east-1' + random.choice(('a','b','c','d'))

        print "Creating temporary %s GB volume in availability zone: %s" % \
                (str(self.size), availability_zone)
        sys.stdout.flush()
        if is_demo:
            time.sleep(10)
            snap_id = 'snap-aaaa1111'
            print "DEMO Snapshot of volume %s created: %s" % \
                    ( 'vol-aaaa1111', snap_id )
            sys.stdout.flush()
            self.latest_snapshot_id = snap_id
            self.save()
            self.cluster_template.status = 'stopped'
            self.cluster_template.save()
        else:
            star_cluster = scwrapper.Cluster(
                self.cluster_template,
                availability_zone,
                )

            volume_id = str(star_cluster.createvolume(self.size, availability_zone))
            print "Temporary volume was created with volume ID: %s" % volume_id
            sys.stdout.flush()
            conn = EC2Connection(aws_key_id, aws_secret_key)
            snapshot = conn.create_snapshot(
                    volume_id,
                    "Initial snapshot for cluster: %s" % star_cluster.cluster_name
                    )
            print "Snapshot of volume %s created: %s" % \
                    ( volume_id, snapshot.id )
            sys.stdout.flush()
            self.latest_snapshot_id = snapshot.id
            self.save()
            conn.delete_volume(volume_id)
            print "Deleted temporary volume: %s" % volume_id
            sys.stdout.flush()

            self.cluster_template.status = 'stopped'
            self.cluster_template.save()
            print "Create initial snapshot done running..."
            sys.stdout.flush()
        return "finished"


class Ec2EbsVolume(models.Model):
    """
    volume_id is like vol-4b843f22
    Some Volumes are from snapshots, some aren't, those that are store the
    original snapshot IDs.  Making it a model relationship didn't seem 
    appropriate.
    """
    disk             = models.ForeignKey('Disk')
    creation_time    = models.DateTimeField()
    destruction_time = models.DateTimeField(blank=True, null=True)
    volume_id        = models.CharField(max_length = 20)
    from_snapshot_id = models.CharField(max_length = 20, blank = True, null = True)
    
class Ec2EbsSnapshot(models.Model):
    """
    snapshot_id is like snap-ed4e4d85
    All snapshots are from volumes, however those volumes may no longer exist in
    EC2, though they should remain in the model.
    """
    disk             = models.ForeignKey('Disk')
    ec2_ebs_volume   = models.ForeignKey('Ec2EbsVolume')
    creation_time    = models.DateTimeField()
    destruction_time = models.DateTimeField(blank=True, null=True)
    snapshot_id      = models.CharField(max_length = 20)

class Ec2Instance(models.Model):
    """
    A Cluster Node or other EC2 Instance
    These will get created when a cluster is launched with the information
    coming from the StarCluster Node instances.
    """
    cluster_instance   = models.ForeignKey('ClusterInstance')
    instance_type      = models.ForeignKey('Ec2InstanceType')
    alias              = models.CharField(max_length = 32)
    arch               = models.CharField(max_length = 32)
    instance_id        = models.CharField(max_length = 16)
    image_id           = models.CharField(max_length = 16)
    launch_time        = models.DateTimeField()
    termination_time   = models.DateTimeField(blank=True, null=True)
    placement          = models.CharField(max_length = 32)
    ip_address         = models.IPAddressField()
    dns_name           = models.CharField(max_length = 256)
    private_ip_address = models.IPAddressField()
    public_dns_name    = models.CharField(max_length = 256)
    state              = models.CharField(max_length = 16)

# Register Django Background Tasks
register_task(Disk.make_initial_snapshot, '''Creates the initial Snapshot.''')
register_task(ClusterInstance.launch, '''Launches the Cluster.''')
register_task(ClusterInstance.terminate, '''Terminates the Cluster.''')
