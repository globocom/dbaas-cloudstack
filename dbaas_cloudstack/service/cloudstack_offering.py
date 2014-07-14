from django_services import service
from ..models import CloudStackOffering


class CloudStackOferringService(service.CRUDService):
    model_class = CloudStackOffering
