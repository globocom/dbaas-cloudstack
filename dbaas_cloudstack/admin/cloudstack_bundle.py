# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.contrib import admin


class CloudStackbundleAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = ("name","zoneid", "templateid", "networkid")
    save_on_top = True
