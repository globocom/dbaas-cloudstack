# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import os
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
    serviceofferingid = models.CharField(verbose_name=_("Offering ID"), max_length=100, help_text="Cloud Stack Offering ID")
    name = models.CharField(verbose_name=_("Name"), max_length=100, help_text="Cloud Stack Offering name")
    weaker = models.BooleanField(verbose_name=_("Is the weaker offering"), default=False)
    region = models.ForeignKey('CloudStackRegion', related_name="cs_offering_region", null=True)
    equivalent_offering = models.ForeignKey('CloudStackOffering', null=True, blank=True, on_delete=models.SET_NULL)
    cpus = models.IntegerField(verbose_name=_("Number of CPUs"), default=0,)
    memory_size_mb = models.IntegerField(verbose_name=_("Memory (MB)"), default=0,)


class CloudStackBundle(BaseModel):
    zoneid = models.CharField(verbose_name=_("Zone ID"), max_length=100, help_text="Cloud Stack Template ID")
    templateid = models.CharField(verbose_name=_("Template ID"), max_length=100, help_text="Cloud Stack Template ID")
    networkid = models.CharField(verbose_name=_("Network ID"), max_length=100, help_text="Cloud Stack Network ID")
    name = models.CharField(verbose_name=_("Name"), max_length=100, help_text="Cloud Stack Zone Name")
    region = models.ForeignKey('CloudStackRegion', related_name="cs_bundle_region", null=True)
    is_active = models.BooleanField(verbose_name=_("Is bundle active"), default=True)
    engine = models.ForeignKey('physical.Engine', null=True, blank=True)

    def __unicode__(self):
        if self.is_active:
            sufix = ''
        else:
            sufix = ' (inactive)'
        return self.name + sufix


class CloudStackRegion(BaseModel):
    name = models.CharField(verbose_name=_("Name"), max_length=100, help_text="Cloud Stack Region Name")
    environment = models.ForeignKey('physical.Environment', related_name="cs_environment_region")


class HostAttr(BaseModel):
    vm_id = models.CharField(verbose_name=_("Cloud Stack vm id"), max_length=255, blank=True, null=True)
    vm_user = models.CharField(verbose_name=_("Cloud Stack virtual machine user"), max_length=255, blank=True, null=True)
    vm_password = EncryptedCharField(verbose_name=_("Cloud Stack virtual machine password"), max_length=255, blank=True, null=True)
    host = models.ForeignKey('physical.Host', related_name="cs_host_attributes")
    bundle = models.ForeignKey(
        CloudStackBundle, null=True, blank=True, on_delete=models.SET_NULL
    )

    def __unicode__(self):
        return "Cloud Stack host Attributes (host=%s)" % (self.host)

    class Meta:
        permissions = (
            ("view_cshostattribute", "Can view cloud stack host attributes"),
        )
        verbose_name_plural = "CloudStack Custom Host Attributes"

    def update_bundle(self):
        from dbaas_cloudstack.provider import CloudStackProvider
        from dbaas_cloudstack.util import get_cs_credential

        databaseinfra = self.host.instances.all()[0].databaseinfra
        environment = databaseinfra.environment
        engine = databaseinfra.engine

        cs_credentials = get_cs_credential(environment)
        cs_provider = CloudStackProvider(credentials=cs_credentials)

        networkid = cs_provider.get_vm_network_id(
            vm_id=self.vm_id,
            project_id=cs_credentials.project)

        zoneid = cs_provider.get_vm_zone_id(
            vm_id=self.vm_id,
            project_id=cs_credentials.project)

        bunbdles = CloudStackBundle.objects.filter(
            networkid=networkid,
            zoneid=zoneid,
            engine=engine,
            region__environment=environment)
        if len(bunbdles) > 0:
            self.bundle = bunbdles[0]
            self.save()


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
    equivalent_dbinfraattr = models.ForeignKey('DatabaseInfraAttr', null=True, blank=True, on_delete=models.SET_NULL)

    def __unicode__(self):
        return "Cloud Stack reserved ip for %s" % (self.databaseinfra)

    class Meta:
        permissions = (
            ("view_csdatabaseinfraattribute", "Can view cloud stack databaseinfra attributes"),
        )
        verbose_name_plural = "CloudStack Custom DatabaseInfra Attributes"

class BundleGroup(BaseModel):
    name = models.CharField(max_length=100)
    bundles = models.ManyToManyField(CloudStackBundle)


class OfferingGroup(BaseModel):
    name = models.CharField(max_length=100)
    offerings = models.ManyToManyField(CloudStackOffering)


class PlanAttr(BaseModel):
    offering_group = models.ForeignKey(OfferingGroup, null=True, blank=True)
    plan = models.ForeignKey('physical.Plan', related_name="cs_plan_attributes")
    bundle_group = models.ForeignKey(BundleGroup, null=True, blank=True)

    @property
    def bundles(self):
        return self.bundle_group.bundles.all()

    @property
    def bundles_actives(self):
        return self.bundle_group.bundles.filter(is_active=True)

    @property
    def offerings(self):
        return self.offering_group.offerings.all()

    def __unicode__(self):
        return "Cloud Stack plan custom Attributes (plan=%s)" % (self.plan)

    def get_weaker_offering(self):
        try:
            offering = self.offerings.get(weaker=True)
        except (ObjectDoesNotExist, MultipleObjectsReturned) as e:
            LOG.warn(e)
            return None
        else:
            return offering

    def get_stronger_offering(self):
        try:
            offering = self.offerings.get(weaker=False)
        except (ObjectDoesNotExist, MultipleObjectsReturned) as e:
            LOG.warn(e)
            return None
        else:
            return offering

    class Meta:
        permissions = (
            ("view_csplanattribute", "Can view cloud stack plan custom attributes"),
        )
        verbose_name_plural = "CloudStack Custom Plan Attributes"


class BundleModel(BaseModel):

    class Meta:
        abstract = True

    @classmethod
    def get_randon_bundle_index(cls, bundles):
        import random
        return random.randint(0, len(bundles) - 1)

    @classmethod
    def get_next_bundle(cls, current_bundle, bundles):
        sorted_bundles = sorted(bundles, key=lambda b: b.id)
        try:
            next_bundle = (i for i, v in enumerate(sorted_bundles) if v.id > current_bundle.id).next()
        except StopIteration:
            next_bundle = 0
        return sorted_bundles[next_bundle]


class LastUsedBundle(BundleModel):
    plan = models.ForeignKey('physical.Plan', related_name="cs_history_plan")
    bundle = models.ForeignKey('CloudStackBundle', related_name="cs_history_bundle")

    class Meta:
        unique_together = (("plan", "bundle"),)

    def __unicode__(self):
        return "Last bundle: %s used for plan: plan %s" % (self.bundle, self.plan)

    @classmethod
    def get_next_infra_bundle(cls, plan, bundles):
        randon_bundle = bundles[cls.get_randon_bundle_index(bundles)]
        try:
            obj, created = cls.objects.get_or_create(
                plan=plan,
                defaults={'plan': plan, 'bundle': randon_bundle},
            )

        except MultipleObjectsReturned as e:
            error = "Multiple objects returned: {}".format(e)
            LOG.warn(error)
            raise Exception(error)

        else:

            if not created:
                obj.bundle = cls.get_next_bundle(current_bundle=obj.bundle,
                                                 bundles=bundles)
                obj.save()
            return obj.bundle


class LastUsedBundleDatabaseInfra(BundleModel):
    databaseinfra = models.ForeignKey('physical.DatabaseInfra',
                                      related_name="cs_history_databaseinfra",
                                      unique=True,)
    bundle = models.ForeignKey('CloudStackBundle',
                               related_name="cs_last_bundle_databaseinfra")

    def __unicode__(self):
        return "Last bundle: {} used for databaseinfra: {}".format(
            self.bundle,
            self.databaseinfra)

    @classmethod
    def get_next_infra_bundle(cls, databaseinfra):
        plan = PlanAttr.objects.get(plan=databaseinfra.plan)
        bundles = list(plan.bundles.filter(is_active=True))
        randon_bundle = bundles[cls.get_randon_bundle_index(bundles)]

        obj, created = cls.objects.get_or_create(
            databaseinfra=databaseinfra,
            defaults={'databaseinfra': databaseinfra, 'bundle': randon_bundle},
        )

        if not created:
            obj.bundle = cls.get_next_bundle(current_bundle=obj.bundle,
                                             bundles=bundles)
            obj.save()
        return obj.bundle

    @classmethod
    def set_last_infra_bundle(cls, databaseinfra, bundle):
        obj, created = cls.objects.get_or_create(
            databaseinfra=databaseinfra,
            defaults={'databaseinfra': databaseinfra, 'bundle': bundle},
        )
        if not created:
            obj.bundle = bundle
            obj.save()


class CloudStackPack(BaseModel):
    offering = models.ForeignKey('CloudStackOffering', related_name="cs_offering_packs")
    engine_type = models.ForeignKey('physical.EngineType', verbose_name=_("Engine Type"), related_name='cs_packs')
    name = models.CharField(verbose_name=_("Name"), max_length=100, help_text="Cloud Stack Pack Name")
    script_file = models.CharField(
        verbose_name=_("Script"), max_length=300, help_text="Full file path",
        null=True, blank=True
    )

    def __unicode__(self):
        return "%s" % (self.name)

    @property
    def get_region(self):
        return self.offering.region

    @property
    def get_environment(self):
        return self.offering.region.environment

    @property
    def script_template(self):
        if not self.script_file:
            return ""

        with open(self.script_file) as f:
            return f.read()


simple_audit.register(PlanAttr)
simple_audit.register(HostAttr)
simple_audit.register(DatabaseInfraAttr)
simple_audit.register(CloudStackBundle)
simple_audit.register(CloudStackOffering)
simple_audit.register(LastUsedBundle)
simple_audit.register(CloudStackRegion)
simple_audit.register(DatabaseInfraOffering)
simple_audit.register(CloudStackPack)
simple_audit.register(BundleGroup)
simple_audit.register(OfferingGroup)
