# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.contrib import admin


class CloudStackRegionAdmin(admin.ModelAdmin):
    search_fields = ("name","environment__name")
    list_display = ("name","environment",)
    save_on_top = True
