# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.contrib import admin


class CloudStackZoneAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = ("zoneid", "name", )
    save_on_top = True
