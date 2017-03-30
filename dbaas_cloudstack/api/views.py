import json
from django.views.generic import View
from django.http import HttpResponse
from dbaas_cloudstack.models import CloudStackBundle


class BundleApi(View):

    def get(self, *args, **kw):
        engine_id = self.kwargs.get('engine_id')
        bundles = CloudStackBundle.objects.filter(engine_id=engine_id).values('id', 'name')

        return HttpResponse(json.dumps(list(bundles)), content_type='application/json')
