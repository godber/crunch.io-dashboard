from piston.handler import BaseHandler
from dash.cluster.models import Disk

class DiskHandler(BaseHandler):
    
    allowed_methods = ('GET', 'PUT', )
    model = Disk   

    # Fields ending with id are omitted
    def read(self, request, id):
        disk = Disk.objects.get(pk=id)
        return disk

    # Use PUT to update, use application username/password
    # curl -v -X PUT -d'latest_snapshot_id=snap-1234abcd' \
    #       -u USER:PASSWORD
    #       http://localhost:8000/api/disk/1/
    def update(self, request, id):
        disk = Disk.objects.get(pk=id)
        disk.latest_snapshot_id = request.PUT.get('latest_snapshot_id')
        disk.save()
        return disk

