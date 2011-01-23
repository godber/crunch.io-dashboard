# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'ClusterTemplate.archived'
        db.add_column('cluster_clustertemplate', 'archived', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'ClusterTemplate.archived'
        db.delete_column('cluster_clustertemplate', 'archived')


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
            'archived': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'creation_time': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_demo': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'number_of_nodes': ('django.db.models.fields.IntegerField', [], {}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'type_of_nodes': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cluster.Ec2InstanceType']"}),
            'user_clustertemplate_id': ('django.db.models.fields.IntegerField', [], {}),
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
            'next_user_clustertemplate_id': ('django.db.models.fields.IntegerField', [], {}),
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
