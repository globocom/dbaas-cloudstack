# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'CloudStackNetwork'
        db.create_table(u'dbaas_cloudstack_cloudstacknetwork', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('networkid', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'dbaas_cloudstack', ['CloudStackNetwork'])

        # Adding model 'CloudStackTemplate'
        db.create_table(u'dbaas_cloudstack_cloudstacktemplate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('templateid', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'dbaas_cloudstack', ['CloudStackTemplate'])

        # Adding model 'CloudStackOffering'
        db.create_table(u'dbaas_cloudstack_cloudstackoffering', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('serviceofferingid', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('weaker', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'dbaas_cloudstack', ['CloudStackOffering'])

        # Adding model 'CloudStackZone'
        db.create_table(u'dbaas_cloudstack_cloudstackzone', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('zoneid', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'dbaas_cloudstack', ['CloudStackZone'])

        # Deleting field 'PlanAttr.networkid'
        db.delete_column(u'dbaas_cloudstack_planattr', 'networkid')

        # Deleting field 'PlanAttr.templateid'
        db.delete_column(u'dbaas_cloudstack_planattr', 'templateid')

        # Deleting field 'PlanAttr.zoneid'
        db.delete_column(u'dbaas_cloudstack_planattr', 'zoneid')

        # Deleting field 'PlanAttr.serviceofferingid'
        db.delete_column(u'dbaas_cloudstack_planattr', 'serviceofferingid')

        # Adding M2M table for field serviceofferingid on 'PlanAttr'
        m2m_table_name = db.shorten_name(u'dbaas_cloudstack_planattr_serviceofferingid')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('planattr', models.ForeignKey(orm[u'dbaas_cloudstack.planattr'], null=False)),
            ('cloudstackoffering', models.ForeignKey(orm[u'dbaas_cloudstack.cloudstackoffering'], null=False))
        ))
        db.create_unique(m2m_table_name, ['planattr_id', 'cloudstackoffering_id'])

        # Adding M2M table for field templateid on 'PlanAttr'
        m2m_table_name = db.shorten_name(u'dbaas_cloudstack_planattr_templateid')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('planattr', models.ForeignKey(orm[u'dbaas_cloudstack.planattr'], null=False)),
            ('cloudstacktemplate', models.ForeignKey(orm[u'dbaas_cloudstack.cloudstacktemplate'], null=False))
        ))
        db.create_unique(m2m_table_name, ['planattr_id', 'cloudstacktemplate_id'])

        # Adding M2M table for field zoneid on 'PlanAttr'
        m2m_table_name = db.shorten_name(u'dbaas_cloudstack_planattr_zoneid')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('planattr', models.ForeignKey(orm[u'dbaas_cloudstack.planattr'], null=False)),
            ('cloudstackzone', models.ForeignKey(orm[u'dbaas_cloudstack.cloudstackzone'], null=False))
        ))
        db.create_unique(m2m_table_name, ['planattr_id', 'cloudstackzone_id'])

        # Adding M2M table for field networkid on 'PlanAttr'
        m2m_table_name = db.shorten_name(u'dbaas_cloudstack_planattr_networkid')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('planattr', models.ForeignKey(orm[u'dbaas_cloudstack.planattr'], null=False)),
            ('cloudstacknetwork', models.ForeignKey(orm[u'dbaas_cloudstack.cloudstacknetwork'], null=False))
        ))
        db.create_unique(m2m_table_name, ['planattr_id', 'cloudstacknetwork_id'])


    def backwards(self, orm):
        # Deleting model 'CloudStackNetwork'
        db.delete_table(u'dbaas_cloudstack_cloudstacknetwork')

        # Deleting model 'CloudStackTemplate'
        db.delete_table(u'dbaas_cloudstack_cloudstacktemplate')

        # Deleting model 'CloudStackOffering'
        db.delete_table(u'dbaas_cloudstack_cloudstackoffering')

        # Deleting model 'CloudStackZone'
        db.delete_table(u'dbaas_cloudstack_cloudstackzone')

        # Adding field 'PlanAttr.networkid'
        db.add_column(u'dbaas_cloudstack_planattr', 'networkid',
                      self.gf('django.db.models.fields.CharField')(default='Reset', max_length=100),
                      keep_default=False)

        # Adding field 'PlanAttr.templateid'
        db.add_column(u'dbaas_cloudstack_planattr', 'templateid',
                      self.gf('django.db.models.fields.CharField')(default='Reset', max_length=100),
                      keep_default=False)

        # Adding field 'PlanAttr.zoneid'
        db.add_column(u'dbaas_cloudstack_planattr', 'zoneid',
                      self.gf('django.db.models.fields.CharField')(default='Reset', max_length=100),
                      keep_default=False)

        # Adding field 'PlanAttr.serviceofferingid'
        db.add_column(u'dbaas_cloudstack_planattr', 'serviceofferingid',
                      self.gf('django.db.models.fields.CharField')(default='Reset', max_length=100),
                      keep_default=False)

        # Removing M2M table for field serviceofferingid on 'PlanAttr'
        db.delete_table(db.shorten_name(u'dbaas_cloudstack_planattr_serviceofferingid'))

        # Removing M2M table for field templateid on 'PlanAttr'
        db.delete_table(db.shorten_name(u'dbaas_cloudstack_planattr_templateid'))

        # Removing M2M table for field zoneid on 'PlanAttr'
        db.delete_table(db.shorten_name(u'dbaas_cloudstack_planattr_zoneid'))

        # Removing M2M table for field networkid on 'PlanAttr'
        db.delete_table(db.shorten_name(u'dbaas_cloudstack_planattr_networkid'))


    models = {
        u'dbaas_cloudstack.cloudstacknetwork': {
            'Meta': {'object_name': 'CloudStackNetwork'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'networkid': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'dbaas_cloudstack.cloudstackoffering': {
            'Meta': {'object_name': 'CloudStackOffering'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'serviceofferingid': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'weaker': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'dbaas_cloudstack.cloudstacktemplate': {
            'Meta': {'object_name': 'CloudStackTemplate'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'templateid': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'dbaas_cloudstack.cloudstackzone': {
            'Meta': {'object_name': 'CloudStackZone'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'zoneid': ('django.db.models.fields.CharField', [], {'max_length': '100'})
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
        u'dbaas_cloudstack.planattr': {
            'Meta': {'object_name': 'PlanAttr'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'networkid': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['dbaas_cloudstack.CloudStackNetwork']", 'symmetrical': 'False'}),
            'plan': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'cs_plan_attributes'", 'to': u"orm['physical.Plan']"}),
            'serviceofferingid': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['dbaas_cloudstack.CloudStackOffering']", 'symmetrical': 'False'}),
            'templateid': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['dbaas_cloudstack.CloudStackTemplate']", 'symmetrical': 'False'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'userdata': ('django.db.models.fields.TextField', [], {}),
            'zoneid': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['dbaas_cloudstack.CloudStackZone']", 'symmetrical': 'False'})
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
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'physical.host': {
            'Meta': {'object_name': 'Host'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
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