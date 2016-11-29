# -*- coding: utf-8 -*-
from django import forms
from django.contrib.admin.helpers import ActionForm


class CloudStackBundleActionForm(ActionForm):
    ZONE_FIELD = 'zoneid'
    TEMPLATE_FIELD = 'templateid'
    NETWORK_FIELD = 'networkid'
    FIELDS = (
        (ZONE_FIELD, 'Zone'),
        (TEMPLATE_FIELD, 'Template'),
        (NETWORK_FIELD, 'Network'),
    )

    field = forms.ChoiceField(choices=FIELDS, required=True, label='Field: ')
    value = forms.CharField(required=True, label='Value: ')

