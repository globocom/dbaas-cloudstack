# -*- coding:utf-8 -*-
from django.contrib import admin
from .cloudstack_serviceoffering import CloudStackServiceofferingAdmin
from .cloudstack_bundle import CloudStackBundleAdmin
from .. import models

admin.site.register(models.CloudStackOffering, CloudStackServiceofferingAdmin)
admin.site.register(models.CloudStackBundle, CloudStackBundleAdmin)
