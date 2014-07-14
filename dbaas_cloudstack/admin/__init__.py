# -*- coding:utf-8 -*-
from django.contrib import admin
from .cloudstack_network import CloudStackNetworkAdmin
from .cloudstack_serviceoffering import CloudStackServiceofferingAdmin
from .cloudstack_template import CloudStackTemplateAdmin
from .cloudstack_zone import CloudStackZoneAdmin
from .. import models

admin.site.register(models.CloudStackNetwork, CloudStackNetworkAdmin)
admin.site.register(models.CloudStackOffering, CloudStackServiceofferingAdmin)
admin.site.register(models.CloudStackTemplate, CloudStackTemplateAdmin)
admin.site.register(models.CloudStackZone, CloudStackZoneAdmin)
