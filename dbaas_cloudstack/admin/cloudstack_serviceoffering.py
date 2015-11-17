# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.contrib import admin


class CloudStackServiceofferingAdmin(admin.ModelAdmin):
    search_fields = ("name", "region__name")
    list_display = ("serviceofferingid", "name", "region", "cpus", "memory_size_mb")
    list_filter = ("region", )
    save_on_top = True
