#!/usr/bin/env python
# -*- coding: utf-8 -*-
from mock import patch
from unittest import TestCase
from django.test import Client


class GetTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = Client()

    @patch('dbaas_cloudstack.api.views.CloudStackBundle.objects.filter')
    def test_pass_id_from_get(self, filter_mock):
        resp = self.client.get('/api/bundles/999/')

        self.assertEqual(resp.status_code, 200)
        self.assertTrue(filter_mock.called)
        self.assertEqual(filter_mock.call_args[1]['engine_id'], '999')

    @patch('dbaas_cloudstack.api.views.CloudStackBundle.objects.filter.values')
    def test_return_status_200_when_no_bundles_found(self, values_mock):

        values_mock.return_value = []
        resp = self.client.get('/api/bundles/33/')

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content, '[]')
