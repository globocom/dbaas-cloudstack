# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.contrib import admin
from dbaas_cloudstack.forms.cloudstack_bundle import CloudStackBundleActionForm


def update_field_value(modeladmin, request, queryset):
    field = request.POST['field']
    value = request.POST['value']
    queryset.update(**{field: value})


class CloudStackBundleAdmin(admin.ModelAdmin):
    search_fields = ("name", "region__name", "zoneid", "templateid", "networkid")
    list_display = ("name", "zoneid", "templateid", "networkid", "region")
    list_filter = ("region", )
    save_on_top = True
    action_form = CloudStackBundleActionForm
    actions = [update_field_value]

    def get_actions(self, request):
        actions = super(CloudStackBundleAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions
