# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.contrib import admin


class CloudStackBundleAdmin(admin.ModelAdmin):
    search_fields = ("name", "region__name")
    list_display = ("name", "zoneid", "templateid", "networkid", "region")
    list_filter = ("region", )
    save_on_top = True
