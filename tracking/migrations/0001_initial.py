# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Visitor'
        db.create_table(u'tracking_visitor', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('session_key', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('ip_address', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
            ('user_agent', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('referrer', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('page_views', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('session_start', self.gf('django.db.models.fields.DateTimeField')()),
            ('last_update', self.gf('django.db.models.fields.DateTimeField')()),
            ('acquisition_source', self.gf('django.db.models.fields.CharField')(default='direct', max_length=255)),
            ('acquisition_medium', self.gf('django.db.models.fields.CharField')(default='direct', max_length=255)),
            ('acquisition_term', self.gf('django.db.models.fields.CharField')(default='direct', max_length=255)),
            ('acquisition_content', self.gf('django.db.models.fields.CharField')(default='direct', max_length=255)),
            ('acquisition_campaign', self.gf('django.db.models.fields.CharField')(default='direct', max_length=255)),
            ('acquisition_gclid', self.gf('django.db.models.fields.CharField')(default='direct', max_length=255)),
            ('past_acquisition_info', self.gf('picklefield.fields.PickledObjectField')(default=[])),
            ('date_added', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 8, 11, 0, 0), auto_now_add=True, blank=True)),
            ('last_modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 8, 11, 0, 0), auto_now=True, auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'tracking', ['Visitor'])

        # Adding unique constraint on 'Visitor', fields ['session_key', 'ip_address']
        db.create_unique(u'tracking_visitor', ['session_key', 'ip_address'])

        # Adding model 'UntrackedUserAgent'
        db.create_table(u'tracking_untrackeduseragent', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('keyword', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('date_added', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 8, 11, 0, 0), auto_now_add=True, blank=True)),
            ('last_modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 8, 11, 0, 0), auto_now=True, auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'tracking', ['UntrackedUserAgent'])

        # Adding model 'BannedIP'
        db.create_table(u'tracking_bannedip', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ip_address', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
            ('date_added', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 8, 11, 0, 0), auto_now_add=True, blank=True)),
            ('last_modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 8, 11, 0, 0), auto_now=True, auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'tracking', ['BannedIP'])


    def backwards(self, orm):
        # Removing unique constraint on 'Visitor', fields ['session_key', 'ip_address']
        db.delete_unique(u'tracking_visitor', ['session_key', 'ip_address'])

        # Deleting model 'Visitor'
        db.delete_table(u'tracking_visitor')

        # Deleting model 'UntrackedUserAgent'
        db.delete_table(u'tracking_untrackeduseragent')

        # Deleting model 'BannedIP'
        db.delete_table(u'tracking_bannedip')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'tracking.bannedip': {
            'Meta': {'ordering': "('ip_address',)", 'object_name': 'BannedIP'},
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 8, 11, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 8, 11, 0, 0)', 'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'})
        },
        u'tracking.untrackeduseragent': {
            'Meta': {'ordering': "('keyword',)", 'object_name': 'UntrackedUserAgent'},
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 8, 11, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keyword': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 8, 11, 0, 0)', 'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'})
        },
        u'tracking.visitor': {
            'Meta': {'ordering': "('-last_update',)", 'unique_together': "(('session_key', 'ip_address'),)", 'object_name': 'Visitor'},
            'acquisition_campaign': ('django.db.models.fields.CharField', [], {'default': "'direct'", 'max_length': '255'}),
            'acquisition_content': ('django.db.models.fields.CharField', [], {'default': "'direct'", 'max_length': '255'}),
            'acquisition_gclid': ('django.db.models.fields.CharField', [], {'default': "'direct'", 'max_length': '255'}),
            'acquisition_medium': ('django.db.models.fields.CharField', [], {'default': "'direct'", 'max_length': '255'}),
            'acquisition_source': ('django.db.models.fields.CharField', [], {'default': "'direct'", 'max_length': '255'}),
            'acquisition_term': ('django.db.models.fields.CharField', [], {'default': "'direct'", 'max_length': '255'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 8, 11, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 8, 11, 0, 0)', 'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {}),
            'page_views': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'past_acquisition_info': ('picklefield.fields.PickledObjectField', [], {'default': '[]'}),
            'referrer': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'session_key': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'session_start': ('django.db.models.fields.DateTimeField', [], {}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True'}),
            'user_agent': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['tracking']