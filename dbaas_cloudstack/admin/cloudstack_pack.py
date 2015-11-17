# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.contrib import admin


class CloudStackPackAdmin(admin.ModelAdmin):
    search_fields = ("offering__name", "engine_type__name", )
    list_display = ("name", "offering", "pack_region", "pack_environment", "engine_type")
    list_filter = ("engine_type", "offering__region__environment")
    save_on_top = True

    def pack_region(self, pack):
        return pack.region.name

    pack_region.short_description = "Region"

    def pack_environment(self, pack):
        return pack.environment.name

    pack_environment.short_description = "Environment"
