# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'CloudStackOffering.equivalent_offering'
        db.alter_column(u'dbaas_cloudstack_cloudstackoffering', 'equivalent_offering_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dbaas_cloudstack.CloudStackOffering'], null=True))

    def backwards(self, orm):

        # Changing field 'CloudStackOffering.equivalent_offering'
        db.alter_column(u'dbaas_cloudstack_cloudstackoffering', 'equivalent_offering_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dbaas_cloudstack.CloudStackRegion'], null=True))

    models = {
        u'dbaas_cloudstack.cloudstackbundle': {
            'Meta': {'object_name': 'CloudStackBundle'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'networkid': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'cs_bundle_region'", 'null': 'True', 'to': u"orm['dbaas_cloudstack.CloudStackRegion']"}),
            'templateid': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'zoneid': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'dbaas_cloudstack.cloudstackoffering': {
            'Meta': {'object_name': 'CloudStackOffering'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'equivalent_offering': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dbaas_cloudstack.CloudStackOffering']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'cs_offering_region'", 'null': 'True', 'to': u"orm['dbaas_cloudstack.CloudStackRegion']"}),
            'serviceofferingid': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'weaker': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'dbaas_cloudstack.cloudstackpack': {
            'Meta': {'object_name': 'CloudStackPack'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'engine_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'cs_packs'", 'to': u"orm['physical.EngineType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'offering': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'cs_offering_packs'", 'to': u"orm['dbaas_cloudstack.CloudStackOffering']"}),
            'script': ('django.db.models.fields.TextField', [], {}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'dbaas_cloudstack.cloudstackregion': {
            'Meta': {'object_name': 'CloudStackRegion'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'environment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'cs_environment_region'", 'to': u"orm['physical.Environment']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'dbaas_cloudstack.databaseinfraattr': {
            'Meta': {'object_name': 'DatabaseInfraAttr'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'cs_ip_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'databaseinfra': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'cs_dbinfra_attributes'", 'to': u"orm['physical.DatabaseInfra']"}),
            'dns': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'is_write': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'networkapi_equipment_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'networkapi_ip_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'dbaas_cloudstack.databaseinfraoffering': {
            'Meta': {'object_name': 'DatabaseInfraOffering'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'databaseinfra': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'cs_dbinfra_offering'", 'to': u"orm['physical.DatabaseInfra']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'offering': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'cs_offering'", 'to': u"orm['dbaas_cloudstack.CloudStackOffering']"}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'dbaas_cloudstack.hostattr': {
            'Meta': {'object_name': 'HostAttr'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'host': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'cs_host_attributes'", 'to': u"orm['physical.Host']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'vm_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'vm_password': ('django.db.models.fields.CharField', [], {'max_length': '406', 'null': 'True', 'blank': 'True'}),
            'vm_user': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'dbaas_cloudstack.lastusedbundle': {
            'Meta': {'unique_together': "((u'plan', u'bundle'),)", 'object_name': 'LastUsedBundle'},
            'bundle': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'cs_history_bundle'", 'to': u"orm['dbaas_cloudstack.CloudStackBundle']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'plan': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'cs_history_plan'", 'to': u"orm['physical.Plan']"}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'dbaas_cloudstack.planattr': {
            'Meta': {'object_name': 'PlanAttr'},
            'bundle': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['dbaas_cloudstack.CloudStackBundle']", 'symmetrical': 'False'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'plan': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'cs_plan_attributes'", 'to': u"orm['physical.Plan']"}),
            'serviceofferingid': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['dbaas_cloudstack.CloudStackOffering']", 'symmetrical': 'False'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'userdata': ('django.db.models.fields.TextField', [], {})
        },
        u'physical.databaseinfra': {
            'Meta': {'object_name': 'DatabaseInfra'},
            'capacity': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'endpoint': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'endpoint_dns': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'engine': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'databaseinfras'", 'on_delete': 'models.PROTECT', 'to': u"orm['physical.Engine']"}),
            'environment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'databaseinfras'", 'on_delete': 'models.PROTECT', 'to': u"orm['physical.Environment']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '406', 'blank': 'True'}),
            'per_database_size_mbytes': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'plan': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'databaseinfras'", 'on_delete': 'models.PROTECT', 'to': u"orm['physical.Plan']"}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'physical.engine': {
            'Meta': {'unique_together': "((u'version', u'engine_type'),)", 'object_name': 'Engine'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'engine_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'engines'", 'on_delete': 'models.PROTECT', 'to': u"orm['physical.EngineType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'template_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user_data_script': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'physical.enginetype': {
            'Meta': {'object_name': 'EngineType'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'physical.environment': {
            'Meta': {'object_name': 'Environment'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'equivalent_environment': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['physical.Environment']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'physical.host': {
            'Meta': {'object_name': 'Host'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'future_host': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['physical.Host']", 'null': 'True'}),
            'hostname': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'monitor_url': ('django.db.models.fields.URLField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'physical.plan': {
            'Meta': {'object_name': 'Plan'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'engine_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'plans'", 'to': u"orm['physical.EngineType']"}),
            'environments': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['physical.Environment']", 'symmetrical': 'False'}),
            'equivalent_plan': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['physical.Plan']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_default': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_ha': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'max_db_size': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'provider': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['dbaas_cloudstack']