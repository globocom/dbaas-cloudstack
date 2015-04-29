# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging

import simple_audit
from dbaas_cloudstack.util.models import BaseModel
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.fields.encrypted import EncryptedCharField
from django.core.exceptions import MultipleObjectsReturned
from django.core.exceptions import ObjectDoesNotExist


LOG = logging.getLogger(__name__)


class CloudStackOffering(BaseModel):
    serviceofferingid = models.CharField(verbose_name=_("Offering ID"),
                                         max_length=100,
                                         help_text="Cloud Stack Offering ID")
    name = models.CharField(verbose_name=_("Name"),
                                         max_length=100,
                                         help_text="Cloud Stack Offering name")
    weaker = models.BooleanField(verbose_name=_("Is the weaker offering"), default=False)
    region = models.ForeignKey('CloudStackRegion', related_name="cs_offering_region", null=True)
    equivalent_offering = models.ForeignKey('CloudStackOffering', null=True, blank= True, on_delete=models.SET_NULL)


class CloudStackBundle(BaseModel):
    zoneid = models.CharField(verbose_name=_("Zone ID"),
                                             max_length=100,
                                             help_text="Cloud Stack Template ID")
    templateid = models.CharField(verbose_name=_("Template ID"),
                                             max_length=100,
                                             help_text="Cloud Stack Template ID")
    networkid = models.CharField(verbose_name=_("Network ID"),
                             max_length=100,
                             help_text="Cloud Stack Network ID")
    name = models.CharField(verbose_name=_("Name"),
                                             max_length=100,
                                             help_text="Cloud Stack Zone Name")
    region = models.ForeignKey('CloudStackRegion', related_name="cs_bundle_region", null=True)

class CloudStackRegion(BaseModel):
    name = models.CharField(verbose_name=_("Name"),
                 max_length=100,
                 help_text="Cloud Stack Region Name")

    environment = models.ForeignKey('physical.Environment', related_name="cs_environment_region")

class HostAttr(BaseModel):

    vm_id = models.CharField(verbose_name=_("Cloud Stack vm id"), max_length=255, blank=True, null=True)
    vm_user = models.CharField(verbose_name=_("Cloud Stack virtual machine user"), max_length=255, blank=True, null=True)
    vm_password = EncryptedCharField(verbose_name=_("Cloud Stack virtual machine password"), max_length=255, blank=True, null=True)
    host = models.ForeignKey('physical.Host', related_name="cs_host_attributes")

    def __unicode__(self):
        return "Cloud Stack host Attributes (host=%s)" % (self.host)

    class Meta:
        permissions = (
            ("view_cshostattribute", "Can view cloud stack host attributes"),
        )
        verbose_name_plural = "CloudStack Custom Host Attributes"


class DatabaseInfraOffering(BaseModel):

    offering = models.ForeignKey('CloudStackOffering', related_name="cs_offering")
    databaseinfra = models.ForeignKey('physical.DatabaseInfra', related_name="cs_dbinfra_offering")

    def __unicode__(self):
        return "Cloud Stack databaseinfra offering %s for %s" % (self.databaseinfra, self.offering)

    class Meta:
        permissions = (
            ("view_csdatabaseinfraoffering", "Can view cloud stack databaseinfra offering"),
        )
        verbose_name_plural = "CloudStack DatabaseInfra Offering"

class DatabaseInfraAttr(BaseModel):

    ip = models.CharField(verbose_name=_("Cloud Stack reserved ip"), max_length=255, blank=True, null=True)
    dns = models.CharField(verbose_name=_("DNS"), max_length=255, blank=True, null=True)
    cs_ip_id = models.CharField(verbose_name=_("Cloud Stack ip id"), max_length=255, blank=True, null=True)
    is_write = models.BooleanField(verbose_name=_("Is write ip"), default=False)
    databaseinfra = models.ForeignKey('physical.DatabaseInfra', related_name="cs_dbinfra_attributes")
    networkapi_equipment_id = models.CharField(verbose_name=_("NetworkAPI Equipment id"), max_length=255, blank=True, null=True)
    networkapi_ip_id = models.CharField(verbose_name=_("NetworkAPI ip id"), max_length=255, blank=True, null=True)
    equivalent_dbinfraattr = models.ForeignKey('DatabaseInfraAttr', null=True, blank= True, on_delete=models.SET_NULL)


    def __unicode__(self):
        return "Cloud Stack reserved ip for %s" % (self.databaseinfra)

    class Meta:
        permissions = (
            ("view_csdatabaseinfraattribute", "Can view cloud stack databaseinfra attributes"),
        )
        verbose_name_plural = "CloudStack Custom DatabaseInfra Attributes"

class PlanAttr(BaseModel):

    serviceofferingid = models.ManyToManyField(CloudStackOffering)

    plan = models.ForeignKey('physical.Plan', related_name="cs_plan_attributes")

    bundle = models.ManyToManyField(CloudStackBundle)

    userdata = models.TextField(verbose_name=_("User Data"),
                                help_text="Script to create config files")

    def __unicode__(self):
        return "Cloud Stack plan custom Attributes (plan=%s)" % (self.plan)


    def get_weaker_offering(self):
        try:
            offering = self.serviceofferingid.get(weaker=True)
        except (ObjectDoesNotExist,MultipleObjectsReturned) as e:
            LOG.warn(e)
            return None
        else:
            return offering

    def get_stronger_offering(self):
        try:
            offering = self.serviceofferingid.get(weaker=False)
        except (ObjectDoesNotExist,MultipleObjectsReturned) as e:
            LOG.warn(e)
            return None
        else:
            return offering

    class Meta:
        permissions = (
            ("view_csplanattribute", "Can view cloud stack plan custom attributes"),
        )
        verbose_name_plural = "CloudStack Custom Plan Attributes"

class LastUsedBundle(BaseModel):

    plan = models.ForeignKey('physical.Plan', related_name="cs_history_plan")

    bundle = models.ForeignKey('CloudStackBundle', related_name="cs_history_bundle")

    class Meta:
        unique_together = (("plan", "bundle"),)

    def __unicode__(self):
        return "Last bundle: %s used for plan: plan %s" % (self.bundle, self.plan)


    @classmethod
    def get_next_bundle(cls, plan, bundle):
        try:
            obj, created = cls.objects.get_or_create(plan=plan,
                                                     defaults={'plan': plan,
                                                               'bundle': bundle[0],
                                                     },
            )

        except MultipleObjectsReturned as e:
            LOG.warn("Multiple objects returned: %s" % e)
            raise
        else:

            if not created:
                next_bundle = (i for i,v in enumerate(bundle) if v!=obj.bundle).next()
                obj.bundle = bundle[next_bundle]
                obj.save()

            return obj.bundle

class CloudStackPack(BaseModel):
    script = models.TextField(verbose_name=_("Script"),
                                help_text="Script setup database")
    offering = models.ForeignKey('CloudStackOffering', related_name="cs_offering_packs")
    engine_type = models.ForeignKey('physical.EngineType', verbose_name=_("Engine Type"), related_name='cs_packs')
    name = models.CharField(verbose_name=_("Name"),
                 max_length=100,
                 help_text="Cloud Stack Pack Name")

    def __unicode__(self):
        return "%s" % (self.name)

    def get_region(self):
        return self.offering.region

    region = property(get_region)

    def get_environment(self):
         return self.offering.region.environment

    environment = property(get_environment)



simple_audit.register(PlanAttr)
simple_audit.register(HostAttr)
simple_audit.register(DatabaseInfraAttr)
simple_audit.register(CloudStackBundle)
simple_audit.register(CloudStackOffering)
simple_audit.register(LastUsedBundle)
simple_audit.register(CloudStackRegion)
simple_audit.register(DatabaseInfraOffering)
simple_audit.register(CloudStackPack)
