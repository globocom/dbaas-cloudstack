from django_services import service
from ..models import CloudStackPack


class CloudStackPackService(service.CRUDService):
    model_class = CloudStackPack
