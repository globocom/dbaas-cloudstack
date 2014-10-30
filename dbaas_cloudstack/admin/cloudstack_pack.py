# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.contrib import admin


class CloudStackPackAdmin(admin.ModelAdmin):
    search_fields = ("pack_offering", "engine_type", )
    list_display = ("pack_offering","pack_region","pack_environment", "is_ha", "engine_type")
    save_on_top = True

    def pack_region(self, pack):
        return pack.region.name

    pack_region.short_description = "Region"

    def pack_environment(self, pack):
        return pack.environment.name

    pack_environment.short_description = "Environment"

    def pack_offering(self, pack):
        return pack.offering.name

    pack_offering.short_description = "Offering"
