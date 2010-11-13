# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Ec2InstanceType'
        db.create_table('cluster_ec2instancetype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('api_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('memory', self.gf('django.db.models.fields.FloatField')()),
            ('compute_units', self.gf('django.db.models.fields.FloatField')()),
            ('compute_description', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('instance_storage', self.gf('django.db.models.fields.IntegerField')()),
            ('storage_description', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('io_performance', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('architecture', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('hourly_price', self.gf('django.db.models.fields.DecimalField')(max_digits=5, decimal_places=3)),
        ))
        db.send_create_signal('cluster', ['Ec2InstanceType'])

        # Adding model 'UserProfile'
        db.create_table('cluster_userprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], unique=True)),
            ('credit', self.gf('django.db.models.fields.DecimalField')(max_digits=8, decimal_places=2)),
        ))
        db.send_create_signal('cluster', ['UserProfile'])

        # Adding model 'AwsCredential'
        db.create_table('cluster_awscredential', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user_profile', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['cluster.UserProfile'], unique=True)),
            ('aws_user_id', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('aws_email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('ssh_key', self.gf('django_fields.fields.EncryptedTextField')(max_length=101)),
            ('aws_key_id', self.gf('django_fields.fields.EncryptedCharField')(max_length=421)),
            ('aws_secret_key', self.gf('django_fields.fields.EncryptedCharField')(max_length=421)),
        ))
        db.send_create_signal('cluster', ['AwsCredential'])

        # Adding model 'ClusterTemplate'
        db.create_table('cluster_clustertemplate', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user_profile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cluster.UserProfile'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('number_of_nodes', self.gf('django.db.models.fields.IntegerField')()),
            ('type_of_nodes', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cluster.Ec2InstanceType'])),
            ('creation_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('is_demo', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal('cluster', ['ClusterTemplate'])

        # Adding model 'ClusterInstance'
        db.create_table('cluster_clusterinstance', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('cluster_template', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cluster.ClusterTemplate'])),
            ('launch_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('termination_time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('availability_zone', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
        ))
        db.send_create_signal('cluster', ['ClusterInstance'])

        # Adding model 'Disk'
        db.create_table('cluster_disk', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('cluster_template', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cluster.ClusterTemplate'])),
            ('size', self.gf('django.db.models.fields.IntegerField')()),
            ('name', self.gf('django.db.models.fields.CharField')(default='Home', max_length=100)),
            ('mount_path', self.gf('django.db.models.fields.CharField')(default='/home', max_length=100)),
            ('partition', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('latest_snapshot_id', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('home_volume_id', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
        ))
        db.send_create_signal('cluster', ['Disk'])

        # Adding model 'Ec2EbsVolume'
        db.create_table('cluster_ec2ebsvolume', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('disk', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cluster.Disk'])),
            ('creation_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('destruction_time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('volume_id', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('from_snapshot_id', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
        ))
        db.send_create_signal('cluster', ['Ec2EbsVolume'])

        # Adding model 'Ec2EbsSnapshot'
        db.create_table('cluster_ec2ebssnapshot', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('disk', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cluster.Disk'])),
            ('ec2_ebs_volume', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cluster.Ec2EbsVolume'])),
            ('creation_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('destruction_time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('snapshot_id', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal('cluster', ['Ec2EbsSnapshot'])

        # Adding model 'Ec2Instance'
        db.create_table('cluster_ec2instance', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('cluster_instance', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cluster.ClusterInstance'])),
            ('instance_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cluster.Ec2InstanceType'])),
            ('alias', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('arch', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('instance_id', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('image_id', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('launch_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('termination_time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('placement', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('ip_address', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
            ('dns_name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('private_ip_address', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
            ('public_dns_name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=16)),
        ))
        db.send_create_signal('cluster', ['Ec2Instance'])


    def backwards(self, orm):
        
        # Deleting model 'Ec2InstanceType'
        db.delete_table('cluster_ec2instancetype')

        # Deleting model 'UserProfile'
        db.delete_table('cluster_userprofile')

        # Deleting model 'AwsCredential'
        db.delete_table('cluster_awscredential')

        # Deleting model 'ClusterTemplate'
        db.delete_table('cluster_clustertemplate')

        # Deleting model 'ClusterInstance'
        db.delete_table('cluster_clusterinstance')

        # Deleting model 'Disk'
        db.delete_table('cluster_disk')

        # Deleting model 'Ec2EbsVolume'
        db.delete_table('cluster_ec2ebsvolume')

        # Deleting model 'Ec2EbsSnapshot'
        db.delete_table('cluster_ec2ebssnapshot')

        # Deleting model 'Ec2Instance'
        db.delete_table('cluster_ec2instance')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'cluster.awscredential': {
            'Meta': {'object_name': 'AwsCredential'},
            'aws_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'aws_key_id': ('django_fields.fields.EncryptedCharField', [], {'max_length': '421'}),
            'aws_secret_key': ('django_fields.fields.EncryptedCharField', [], {'max_length': '421'}),
            'aws_user_id': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ssh_key': ('django_fields.fields.EncryptedTextField', [], {'max_length': '101'}),
            'user_profile': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cluster.UserProfile']", 'unique': 'True'})
        },
        'cluster.clusterinstance': {
            'Meta': {'object_name': 'ClusterInstance'},
            'availability_zone': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'cluster_template': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cluster.ClusterTemplate']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'launch_time': ('django.db.models.fields.DateTimeField', [], {}),
            'termination_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        'cluster.clustertemplate': {
            'Meta': {'object_name': 'ClusterTemplate'},
            'creation_time': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_demo': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'number_of_nodes': ('django.db.models.fields.IntegerField', [], {}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'type_of_nodes': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cluster.Ec2InstanceType']"}),
            'user_profile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cluster.UserProfile']"})
        },
        'cluster.disk': {
            'Meta': {'object_name': 'Disk'},
            'cluster_template': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cluster.ClusterTemplate']"}),
            'home_volume_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latest_snapshot_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'mount_path': ('django.db.models.fields.CharField', [], {'default': "'/home'", 'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'Home'", 'max_length': '100'}),
            'partition': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'size': ('django.db.models.fields.IntegerField', [], {})
        },
        'cluster.ec2ebssnapshot': {
            'Meta': {'object_name': 'Ec2EbsSnapshot'},
            'creation_time': ('django.db.models.fields.DateTimeField', [], {}),
            'destruction_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'disk': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cluster.Disk']"}),
            'ec2_ebs_volume': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cluster.Ec2EbsVolume']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'snapshot_id': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'cluster.ec2ebsvolume': {
            'Meta': {'object_name': 'Ec2EbsVolume'},
            'creation_time': ('django.db.models.fields.DateTimeField', [], {}),
            'destruction_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'disk': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cluster.Disk']"}),
            'from_snapshot_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'volume_id': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'cluster.ec2instance': {
            'Meta': {'object_name': 'Ec2Instance'},
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'arch': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'cluster_instance': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cluster.ClusterInstance']"}),
            'dns_name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_id': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'instance_id': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'instance_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cluster.Ec2InstanceType']"}),
            'ip_address': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'launch_time': ('django.db.models.fields.DateTimeField', [], {}),
            'placement': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'private_ip_address': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'public_dns_name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'termination_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        'cluster.ec2instancetype': {
            'Meta': {'object_name': 'Ec2InstanceType'},
            'api_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'architecture': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'compute_description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'compute_units': ('django.db.models.fields.FloatField', [], {}),
            'hourly_price': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '3'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instance_storage': ('django.db.models.fields.IntegerField', [], {}),
            'io_performance': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'memory': ('django.db.models.fields.FloatField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'storage_description': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'cluster.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'credit': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['cluster']
