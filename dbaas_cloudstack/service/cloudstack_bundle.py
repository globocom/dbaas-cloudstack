from django_services import service
from ..models import CloudStackBundle


class CloudStackBundleService(service.CRUDService):
    model_class = CloudStackBundle
