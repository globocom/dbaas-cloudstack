from django_services import service
from ..models import CloudStackRegion


class CloudStackRegionService(service.CRUDService):
    model_class = CloudStackRegion
