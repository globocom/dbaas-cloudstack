from django_services import service
from ..models import CloudStackTemplate


class CloudStackTemplateService(service.CRUDService):
    model_class = CloudStackTemplate
