# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'RevenueVisitor.visitor_ptr'
        db.delete_column(u'tracking_revenuevisitor', u'visitor_ptr_id')

        # Adding field 'RevenueVisitor.id'
        db.add_column(u'tracking_revenuevisitor', u'id',
                      self.gf('django.db.models.fields.AutoField')(default=None, primary_key=True),
                      keep_default=False)

        # Adding field 'RevenueVisitor.session_key'
        db.add_column(u'tracking_revenuevisitor', 'session_key',
                      self.gf('django.db.models.fields.CharField')(default=None, max_length=40),
                      keep_default=False)

        # Adding field 'RevenueVisitor.ip_address'
        db.add_column(u'tracking_revenuevisitor', 'ip_address',
                      self.gf('django.db.models.fields.CharField')(default=None, max_length=20),
                      keep_default=False)

        # Adding field 'RevenueVisitor.user'
        db.add_column(u'tracking_revenuevisitor', 'user',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True),
                      keep_default=False)

        # Adding field 'RevenueVisitor.user_agent'
        db.add_column(u'tracking_revenuevisitor', 'user_agent',
                      self.gf('django.db.models.fields.CharField')(default=None, max_length=255),
                      keep_default=False)

        # Adding field 'RevenueVisitor.referrer'
        db.add_column(u'tracking_revenuevisitor', 'referrer',
                      self.gf('django.db.models.fields.CharField')(default=None, max_length=255),
                      keep_default=False)

        # Adding field 'RevenueVisitor.url'
        db.add_column(u'tracking_revenuevisitor', 'url',
                      self.gf('django.db.models.fields.CharField')(default=None, max_length=255),
                      keep_default=False)

        # Adding field 'RevenueVisitor.page_views'
        db.add_column(u'tracking_revenuevisitor', 'page_views',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=0),
                      keep_default=False)

        # Adding field 'RevenueVisitor.session_start'
        db.add_column(u'tracking_revenuevisitor', 'session_start',
                      self.gf('django.db.models.fields.DateTimeField')(default=None),
                      keep_default=False)

        # Adding field 'RevenueVisitor.last_update'
        db.add_column(u'tracking_revenuevisitor', 'last_update',
                      self.gf('django.db.models.fields.DateTimeField')(default=None),
                      keep_default=False)

        # Adding field 'RevenueVisitor.acquisition_source'
        db.add_column(u'tracking_revenuevisitor', 'acquisition_source',
                      self.gf('django.db.models.fields.CharField')(default='direct', max_length=255),
                      keep_default=False)

        # Adding field 'RevenueVisitor.acquisition_medium'
        db.add_column(u'tracking_revenuevisitor', 'acquisition_medium',
                      self.gf('django.db.models.fields.CharField')(default='direct', max_length=255),
                      keep_default=False)

        # Adding field 'RevenueVisitor.acquisition_term'
        db.add_column(u'tracking_revenuevisitor', 'acquisition_term',
                      self.gf('django.db.models.fields.CharField')(default='direct', max_length=255),
                      keep_default=False)

        # Adding field 'RevenueVisitor.acquisition_content'
        db.add_column(u'tracking_revenuevisitor', 'acquisition_content',
                      self.gf('django.db.models.fields.CharField')(default='direct', max_length=255),
                      keep_default=False)

        # Adding field 'RevenueVisitor.acquisition_campaign'
        db.add_column(u'tracking_revenuevisitor', 'acquisition_campaign',
                      self.gf('django.db.models.fields.CharField')(default='direct', max_length=255),
                      keep_default=False)

        # Adding field 'RevenueVisitor.acquisition_gclid'
        db.add_column(u'tracking_revenuevisitor', 'acquisition_gclid',
                      self.gf('django.db.models.fields.CharField')(default='direct', max_length=255),
                      keep_default=False)

        # Adding field 'RevenueVisitor.past_acquisition_info'
        db.add_column(u'tracking_revenuevisitor', 'past_acquisition_info',
                      self.gf('picklefield.fields.PickledObjectField')(default=[]),
                      keep_default=False)

        # Adding field 'RevenueVisitor.date_added'
        db.add_column(u'tracking_revenuevisitor', 'date_added',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 8, 12, 0, 0), auto_now_add=True, blank=True),
                      keep_default=False)

        # Adding field 'RevenueVisitor.last_modified'
        db.add_column(u'tracking_revenuevisitor', 'last_modified',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 8, 12, 0, 0), auto_now=True, auto_now_add=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'RevenueVisitor.visitor_ptr'
        db.add_column(u'tracking_revenuevisitor', u'visitor_ptr',
                      self.gf('django.db.models.fields.related.OneToOneField')(default=None, to=orm['tracking.Visitor'], unique=True, primary_key=True),
                      keep_default=False)

        # Deleting field 'RevenueVisitor.id'
        db.delete_column(u'tracking_revenuevisitor', u'id')

        # Deleting field 'RevenueVisitor.session_key'
        db.delete_column(u'tracking_revenuevisitor', 'session_key')

        # Deleting field 'RevenueVisitor.ip_address'
        db.delete_column(u'tracking_revenuevisitor', 'ip_address')

        # Deleting field 'RevenueVisitor.user'
        db.delete_column(u'tracking_revenuevisitor', 'user_id')

        # Deleting field 'RevenueVisitor.user_agent'
        db.delete_column(u'tracking_revenuevisitor', 'user_agent')

        # Deleting field 'RevenueVisitor.referrer'
        db.delete_column(u'tracking_revenuevisitor', 'referrer')

        # Deleting field 'RevenueVisitor.url'
        db.delete_column(u'tracking_revenuevisitor', 'url')

        # Deleting field 'RevenueVisitor.page_views'
        db.delete_column(u'tracking_revenuevisitor', 'page_views')

        # Deleting field 'RevenueVisitor.session_start'
        db.delete_column(u'tracking_revenuevisitor', 'session_start')

        # Deleting field 'RevenueVisitor.last_update'
        db.delete_column(u'tracking_revenuevisitor', 'last_update')

        # Deleting field 'RevenueVisitor.acquisition_source'
        db.delete_column(u'tracking_revenuevisitor', 'acquisition_source')

        # Deleting field 'RevenueVisitor.acquisition_medium'
        db.delete_column(u'tracking_revenuevisitor', 'acquisition_medium')

        # Deleting field 'RevenueVisitor.acquisition_term'
        db.delete_column(u'tracking_revenuevisitor', 'acquisition_term')

        # Deleting field 'RevenueVisitor.acquisition_content'
        db.delete_column(u'tracking_revenuevisitor', 'acquisition_content')

        # Deleting field 'RevenueVisitor.acquisition_campaign'
        db.delete_column(u'tracking_revenuevisitor', 'acquisition_campaign')

        # Deleting field 'RevenueVisitor.acquisition_gclid'
        db.delete_column(u'tracking_revenuevisitor', 'acquisition_gclid')

        # Deleting field 'RevenueVisitor.past_acquisition_info'
        db.delete_column(u'tracking_revenuevisitor', 'past_acquisition_info')

        # Deleting field 'RevenueVisitor.date_added'
        db.delete_column(u'tracking_revenuevisitor', 'date_added')

        # Deleting field 'RevenueVisitor.last_modified'
        db.delete_column(u'tracking_revenuevisitor', 'last_modified')


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
        u'core.category': {
            'Meta': {'object_name': 'Category'},
            'code': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 8, 12, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 8, 12, 0, 0)', 'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Category']", 'null': 'True', 'blank': 'True'}),
            'ref_id': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'core.country': {
            'Meta': {'object_name': 'Country'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 8, 12, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 8, 12, 0, 0)', 'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'})
        },
        u'core.coupon': {
            'Meta': {'object_name': 'Coupon'},
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['core.Category']", 'null': 'True', 'blank': 'True'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'countries': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['core.Country']", 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 8, 12, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'dealtypes': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['core.DealType']", 'null': 'True', 'blank': 'True'}),
            'desc_slug': ('django.db.models.fields.CharField', [], {'default': "'COUPON'", 'max_length': '175'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'directlink': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'discount': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 8, 12, 0, 0)', 'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'lastupdated': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'link': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'listprice': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'merchant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Merchant']", 'null': 'True', 'blank': 'True'}),
            'percent': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'price': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'ref_id': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'restrictions': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'short_desc': ('django.db.models.fields.CharField', [], {'default': "'COUPON'", 'max_length': '50'}),
            'skimlinks': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'start': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'core.dealtype': {
            'Meta': {'object_name': 'DealType'},
            'code': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 8, 12, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 8, 12, 0, 0)', 'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'core.merchant': {
            'Meta': {'object_name': 'Merchant'},
            'coupon_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 8, 12, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'directlink': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 8, 12, 0, 0)', 'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'link': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'name_slug': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'ref_id': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'skimlinks': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        u'tracking.bannedip': {
            'Meta': {'ordering': "('ip_address',)", 'object_name': 'BannedIP'},
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 8, 12, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 8, 12, 0, 0)', 'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'})
        },
        u'tracking.clicktrack': {
            'Meta': {'object_name': 'ClickTrack'},
            'coupon': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Coupon']", 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2013, 8, 12, 0, 0)'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 8, 12, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 8, 12, 0, 0)', 'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'merchant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Merchant']", 'null': 'True', 'blank': 'True'}),
            'merchant_domain': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'referer': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'source_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'source_url_type': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'target_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'user_agent': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'visitor': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tracking.Visitor']", 'null': 'True', 'blank': 'True'})
        },
        u'tracking.commission': {
            'Meta': {'object_name': 'Commission'},
            'commissionID': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'commissionType': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'commissionValue': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'currency': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'customID': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'domainID': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'items': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'merchantID': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'publisherID': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'remoteReferer': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'remoteUserAgent': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'sales': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'tracking.revenuevisitor': {
            'Meta': {'object_name': 'RevenueVisitor'},
            'acquisition_campaign': ('django.db.models.fields.CharField', [], {'default': "'direct'", 'max_length': '255'}),
            'acquisition_content': ('django.db.models.fields.CharField', [], {'default': "'direct'", 'max_length': '255'}),
            'acquisition_gclid': ('django.db.models.fields.CharField', [], {'default': "'direct'", 'max_length': '255'}),
            'acquisition_medium': ('django.db.models.fields.CharField', [], {'default': "'direct'", 'max_length': '255'}),
            'acquisition_source': ('django.db.models.fields.CharField', [], {'default': "'direct'", 'max_length': '255'}),
            'acquisition_term': ('django.db.models.fields.CharField', [], {'default': "'direct'", 'max_length': '255'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 8, 12, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'date_obj_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 8, 12, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 8, 12, 0, 0)', 'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'last_obj_modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 8, 12, 0, 0)', 'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {}),
            'page_views': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'past_acquisition_info': ('picklefield.fields.PickledObjectField', [], {'default': '[]'}),
            'referrer': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'session_key': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'session_start': ('django.db.models.fields.DateTimeField', [], {}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'user_agent': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'visitor': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'rev_visitor'", 'null': 'True', 'to': u"orm['tracking.Visitor']"})
        },
        u'tracking.untrackeduseragent': {
            'Meta': {'ordering': "('keyword',)", 'object_name': 'UntrackedUserAgent'},
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 8, 12, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keyword': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 8, 12, 0, 0)', 'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'})
        },
        u'tracking.visitor': {
            'Meta': {'ordering': "('-last_update',)", 'unique_together': "(('session_key', 'ip_address'),)", 'object_name': 'Visitor'},
            'acquisition_campaign': ('django.db.models.fields.CharField', [], {'default': "'direct'", 'max_length': '255'}),
            'acquisition_content': ('django.db.models.fields.CharField', [], {'default': "'direct'", 'max_length': '255'}),
            'acquisition_gclid': ('django.db.models.fields.CharField', [], {'default': "'direct'", 'max_length': '255'}),
            'acquisition_medium': ('django.db.models.fields.CharField', [], {'default': "'direct'", 'max_length': '255'}),
            'acquisition_source': ('django.db.models.fields.CharField', [], {'default': "'direct'", 'max_length': '255'}),
            'acquisition_term': ('django.db.models.fields.CharField', [], {'default': "'direct'", 'max_length': '255'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 8, 12, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 8, 12, 0, 0)', 'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {}),
            'page_views': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'past_acquisition_info': ('picklefield.fields.PickledObjectField', [], {'default': '[]'}),
            'referrer': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'session_key': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'session_start': ('django.db.models.fields.DateTimeField', [], {}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'user_agent': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['tracking']