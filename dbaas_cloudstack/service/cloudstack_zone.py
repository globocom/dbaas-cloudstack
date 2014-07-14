from django_services import service
from ..models import CloudStackZone


class CloudStackZoneService(service.CRUDService):
    model_class = CloudStackZone
