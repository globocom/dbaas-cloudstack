from django_services import service
from ..models import CloudStackNetwork


class CloudStackNetworkService(service.CRUDService):
    model_class = CloudStackNetwork
