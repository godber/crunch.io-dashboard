from dash.cluster.models import ClusterTemplate, ClusterInstance 
from dash.cluster.models import UserProfile, AwsCredential
from dash.cluster.models import Disk, Ec2InstanceType
from dash.cluster.models import Ec2EbsVolume, Ec2EbsSnapshot, Ec2Instance
from django.contrib import admin

class ClusterTemplateAdmin(admin.ModelAdmin):
    list_display = ( 
            'name',
            'archived',
            'number_of_nodes',
            'type_of_nodes',
            'status',
            'user_profile',
            )

class ClusterInstanceAdmin(admin.ModelAdmin):
    list_display = ( 'launch_time', 'termination_time', 'cluster_template')

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ( 'user', 'credit' )

class AwsCredentialAdmin(admin.ModelAdmin):
    list_display = (
        'aws_user_id',
        'aws_email',
        'user_profile',
        'aws_key_id',
    )

class DiskAdmin(admin.ModelAdmin):
    list_display = ( 
            'name', 
            'size', 
            'cluster_template', 
            'latest_snapshot_id',
            'home_volume_id' 
            )

class Ec2InstanceTypeAdmin(admin.ModelAdmin):
    list_display = ( 'name', 'api_name', 'memory', 'instance_storage',
            'architecture', 'hourly_price' )

class Ec2EbsVolumeAdmin(admin.ModelAdmin):
    list_display = ( 'volume_id', 'from_snapshot_id', 'creation_time',
            'destruction_time', 'disk' )

class Ec2EbsSnapshotAdmin(admin.ModelAdmin):
    list_display = ( 'snapshot_id', 'creation_time', 'destruction_time', 
            'disk' )

class Ec2InstanceAdmin(admin.ModelAdmin):
    list_display = (
        'cluster_instance',
        'instance_type',
        'alias',
        'arch',
        'placement',
        'ip_address',
        'state'
        )

 

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(AwsCredential, AwsCredentialAdmin)
admin.site.register(ClusterTemplate, ClusterTemplateAdmin)
admin.site.register(ClusterInstance, ClusterInstanceAdmin)
admin.site.register(Disk, DiskAdmin)
admin.site.register(Ec2InstanceType, Ec2InstanceTypeAdmin)
admin.site.register(Ec2EbsVolume, Ec2EbsVolumeAdmin)
admin.site.register(Ec2EbsSnapshot, Ec2EbsSnapshotAdmin)
admin.site.register(Ec2Instance, Ec2InstanceAdmin)
