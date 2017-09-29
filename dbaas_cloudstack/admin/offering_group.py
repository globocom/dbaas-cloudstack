# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from dbaas_cloudstack.models import CloudStackRegion
from dbaas_cloudstack.models import CloudStackOffering

class RegionListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('region')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'region'

    def lookups(self, request, model_admin):

        tuple_list = CloudStackRegion.objects.values_list("name", "name")

        return (
            list(tuple_list)
        )

    def queryset(self, request, queryset):

        if not self.value():
            return

        offerings_list = CloudStackOffering.objects.filter(region__name=self.value())
        acceptable_ids = []

        for offering in offerings_list:
            acceptable_ids.extend(offering.offeringgroup_set.values_list("id", flat=True))

        return queryset.filter(id__in=set(acceptable_ids))


class EnvironmentListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('environment')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'environment'

    def lookups(self, request, model_admin):

        tuple_list = CloudStackRegion.objects.values_list("environment__name", "environment__name")

        return (
            list(tuple_list)
        )

    def queryset(self, request, queryset):

        if not self.value():
            return

        offerings_list = CloudStackOffering.objects.filter(region__environment__name=self.value())
        acceptable_ids = []

        for offering in offerings_list:
            acceptable_ids.extend(offering.offeringgroup_set.values_list("id", flat=True))

        return queryset.filter(id__in=set(acceptable_ids))
        


class OfferingGroupAdmin(admin.ModelAdmin):
    #list_display = ("name",)
    list_filter = (RegionListFilter, EnvironmentListFilter)
