# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.contrib import admin
from physical.models import Engine
from physical.models import Environment
from dbaas_cloudstack.models import CloudStackBundle
from dbaas_cloudstack.util.admin_filters import BaseGroupFilter

class EngineListFilter(BaseGroupFilter):
    title = 'engine'

    parameter_name = 'engine'

    filter_option_queryset = Engine.objects.values_list("engine_type__name", "engine_type__name")

    def get_acceptable_ids(self, value):
        bundles_list = CloudStackBundle.objects.filter(engine__engine_type__name=self.value())
        acceptable_ids = []

        for bundle in bundles_list:
            acceptable_ids.extend(bundle.bundlegroup_set.values_list("id", flat=True))

        return acceptable_ids



class EnvironmentListFilter(BaseGroupFilter):
    title = 'environment'

    parameter_name = 'environment'

    filter_option_queryset = Environment.objects.values_list("name", "name")

    def get_acceptable_ids(self, value):
        
        bundles_list = CloudStackBundle.objects.filter(region__environment__name=self.value())
        acceptable_ids = []

        for bundle in bundles_list:
            acceptable_ids.extend(bundle.bundlegroup_set.values_list("id", flat=True))

        return acceptable_ids


class BundleGroupAdmin(admin.ModelAdmin):
    list_filter = (EngineListFilter, EnvironmentListFilter)

    filter_horizontal = ("bundles",)

    change_form_template = "dbaas_cloudstack/bundlegroup/change_form.html"
    add_form_template = "admin/change_form.html"
