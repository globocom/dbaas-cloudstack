# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.contrib import admin
from dbaas_cloudstack.models import CloudStackRegion
from dbaas_cloudstack.models import CloudStackOffering
from dbaas_cloudstack.util.admin_filters import BaseGroupFilter


class RegionListFilter(BaseGroupFilter):
    title = 'region'

    parameter_name = 'region'

    filter_option_queryset = CloudStackRegion.objects.values_list("name", "name")

    def get_acceptable_ids(self, value):

        offerings_list = CloudStackOffering.objects.filter(region__name=value)
        acceptable_ids = []

        for offering in offerings_list:
            acceptable_ids.extend(offering.offeringgroup_set.values_list("id", flat=True))

        return acceptable_ids


class EnvironmentListFilter(BaseGroupFilter):
    title = 'environment'

    parameter_name = 'environment'

    filter_option_queryset = CloudStackRegion.objects.values_list("environment__name", "environment__name")

    def get_acceptable_ids(self, value):

        offerings_list = CloudStackOffering.objects.filter(region__environment__name=self.value())
        acceptable_ids = []

        for offering in offerings_list:
            acceptable_ids.extend(offering.offeringgroup_set.values_list("id", flat=True))

        return acceptable_ids


class OfferingGroupAdmin(admin.ModelAdmin):
    list_filter = (RegionListFilter, EnvironmentListFilter)

    filter_horizontal = ("offerings",)

    change_form_template = "dbaas_cloudstack/offeringgroup/change_form.html"
    add_form_template = "admin/change_form.html"

    class Media:
        css = {
            "all": ("dbaas_cloudstack/css/bundlegroup-widgets.css",)
        }
