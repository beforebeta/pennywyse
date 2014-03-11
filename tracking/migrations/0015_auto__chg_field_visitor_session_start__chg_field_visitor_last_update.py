# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Visitor.session_start'
        db.alter_column(u'tracking_visitor', 'session_start', self.gf('django.db.models.fields.DateTimeField')(null=True))

        # Changing field 'Visitor.last_update'
        db.alter_column(u'tracking_visitor', 'last_update', self.gf('django.db.models.fields.DateTimeField')(null=True))

    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'Visitor.session_start'
        raise RuntimeError("Cannot reverse this migration. 'Visitor.session_start' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'Visitor.session_start'
        db.alter_column(u'tracking_visitor', 'session_start', self.gf('django.db.models.fields.DateTimeField')())

        # User chose to not deal with backwards NULL issues for 'Visitor.last_update'
        raise RuntimeError("Cannot reverse this migration. 'Visitor.last_update' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'Visitor.last_update'
        db.alter_column(u'tracking_visitor', 'last_update', self.gf('django.db.models.fields.DateTimeField')())

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
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 3, 11, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'icon': ('django.db.models.fields.TextField', [], {'default': "u'/static/img/category_icons/placeholder.jpg'", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.TextField', [], {'default': "u'/static/img/favicon.png'", 'null': 'True', 'blank': 'True'}),
            'is_featured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 3, 11, 0, 0)', 'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'navigation_section': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['web.CategorySection']", 'null': 'True', 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Category']", 'null': 'True', 'blank': 'True'}),
            'ref_id': ('django.db.models.fields.CharField', [], {'default': "u'refid'", 'max_length': '255', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'ref_id_source': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'core.country': {
            'Meta': {'object_name': 'Country'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 3, 11, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 3, 11, 0, 0)', 'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'})
        },
        u'core.coupon': {
            'Meta': {'object_name': 'Coupon'},
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['core.Category']", 'null': 'True', 'blank': 'True'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'countries': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['core.Country']", 'null': 'True', 'blank': 'True'}),
            'coupon_network': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.CouponNetwork']", 'null': 'True', 'blank': 'True'}),
            'coupon_type': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 3, 11, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'dealtypes': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['core.DealType']", 'null': 'True', 'blank': 'True'}),
            'desc_slug': ('django.db.models.fields.CharField', [], {'default': "u'COUPON'", 'max_length': '175'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'directlink': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'discount': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'embedly_description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'embedly_image_url': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'embedly_title': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'featured_in': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'featured'", 'null': 'True', 'to': u"orm['web.TopCouponSection']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_duplicate': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_featured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_new': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_popular': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 3, 11, 0, 0)', 'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'lastupdated': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'link': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'listprice': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'merchant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Merchant']", 'null': 'True', 'blank': 'True'}),
            'merchant_location': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.MerchantLocation']", 'null': 'True', 'blank': 'True'}),
            'online': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'percent': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'popular_in': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'popular'", 'null': 'True', 'to': u"orm['web.TopCouponSection']"}),
            'popularity': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'price': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'ref_id': ('django.db.models.fields.CharField', [], {'default': "u'refid'", 'max_length': '255', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'ref_id_source': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'related_deal': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Coupon']", 'null': 'True', 'blank': 'True'}),
            'restrictions': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            's3_image': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'short_desc': ('django.db.models.fields.CharField', [], {'default': "u'COUPON'", 'max_length': '50'}),
            'skimlinks': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'start': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'core.couponnetwork': {
            'Meta': {'object_name': 'CouponNetwork'},
            'code': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 3, 11, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 3, 11, 0, 0)', 'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '255', 'null': 'True', 'db_index': 'True', 'blank': 'True'})
        },
        u'core.dealtype': {
            'Meta': {'object_name': 'DealType'},
            'code': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 3, 11, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 3, 11, 0, 0)', 'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'core.merchant': {
            'Meta': {'object_name': 'Merchant'},
            'coupon_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 3, 11, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'directlink': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'is_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_featured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 3, 11, 0, 0)', 'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'link': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'name_slug': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'navigation_section': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'stores'", 'null': 'True', 'to': u"orm['web.TopCouponSection']"}),
            'popularity': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'redirect': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'ref_id': ('django.db.models.fields.CharField', [], {'default': "u'refid'", 'max_length': '255', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'ref_id_source': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            's3_image': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'similar': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['core.Merchant']", 'null': 'True', 'blank': 'True'}),
            'skimlinks': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'total_coupon_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'use_skimlinks': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        u'core.merchantlocation': {
            'Meta': {'object_name': 'MerchantLocation'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 3, 11, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'geometry': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 3, 11, 0, 0)', 'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'locality': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'merchant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Merchant']", 'null': 'True', 'blank': 'True'}),
            'postal_code': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'region': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'tracking.acquisitionsource': {
            'Meta': {'ordering': "('tag',)", 'object_name': 'AcquisitionSource'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logo_url': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'tag': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'tracking.adcost': {
            'Meta': {'object_name': 'AdCost'},
            'acquisition_campaign': ('django.db.models.fields.CharField', [], {'default': "'direct'", 'max_length': '255'}),
            'acquisition_medium': ('django.db.models.fields.CharField', [], {'default': "'direct'", 'max_length': '255'}),
            'acquisition_source': ('django.db.models.fields.CharField', [], {'default': "'direct'", 'max_length': '255'}),
            'acquisition_term': ('django.db.models.fields.CharField', [], {'default': "'direct'", 'max_length': '255'}),
            'actions': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'ad': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'average_cpc': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'campaign': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'clicks': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'cost_id': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'costs': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'frequency': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'impression': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'keyword': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'social_clicks': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'social_impression': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'start_date': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'synchronized': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'unique_clicks': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'tracking.bannedip': {
            'Meta': {'ordering': "('ip_address',)", 'object_name': 'BannedIP'},
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 3, 11, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 3, 11, 0, 0)', 'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'})
        },
        u'tracking.clicktrack': {
            'Meta': {'object_name': 'ClickTrack'},
            'acquisition_campaign': ('django.db.models.fields.CharField', [], {'default': "'direct'", 'max_length': '255'}),
            'acquisition_content': ('django.db.models.fields.CharField', [], {'default': "'direct'", 'max_length': '255'}),
            'acquisition_gclid': ('django.db.models.fields.CharField', [], {'default': "'direct'", 'max_length': '255'}),
            'acquisition_medium': ('django.db.models.fields.CharField', [], {'default': "'direct'", 'max_length': '255'}),
            'acquisition_source': ('django.db.models.fields.CharField', [], {'default': "'direct'", 'max_length': '255'}),
            'acquisition_term': ('django.db.models.fields.CharField', [], {'default': "'direct'", 'max_length': '255'}),
            'coupon': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Coupon']", 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2014, 3, 11, 0, 0)'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 3, 11, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 3, 11, 0, 0)', 'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
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
            'customIDAsInt': ('django.db.models.fields.IntegerField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'domainID': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'items': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'merchantID': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'orderValue': ('django.db.models.fields.FloatField', [], {'default': '0'}),
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
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 3, 11, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'date_obj_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 3, 11, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 3, 11, 0, 0)', 'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'last_obj_modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 3, 11, 0, 0)', 'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
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
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 3, 11, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keyword': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 3, 11, 0, 0)', 'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'})
        },
        u'tracking.visitor': {
            'Meta': {'ordering': "('-last_update',)", 'unique_together': "(('session_key', 'ip_address'),)", 'object_name': 'Visitor'},
            'acquisition_campaign': ('django.db.models.fields.CharField', [], {'default': "'direct'", 'max_length': '255'}),
            'acquisition_content': ('django.db.models.fields.CharField', [], {'default': "'direct'", 'max_length': '255'}),
            'acquisition_gclid': ('django.db.models.fields.CharField', [], {'default': "'direct'", 'max_length': '255'}),
            'acquisition_medium': ('django.db.models.fields.CharField', [], {'default': "'direct'", 'max_length': '255'}),
            'acquisition_source': ('django.db.models.fields.CharField', [], {'default': "'direct'", 'max_length': '255'}),
            'acquisition_term': ('django.db.models.fields.CharField', [], {'default': "'direct'", 'max_length': '255'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 3, 11, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 3, 11, 0, 0)', 'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'page_views': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'past_acquisition_info': ('picklefield.fields.PickledObjectField', [], {'default': '[]'}),
            'referrer': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'session_key': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'session_start': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'user_agent': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'web.categorysection': {
            'Meta': {'ordering': "['order']", 'object_name': 'CategorySection'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'order': ('django.db.models.fields.IntegerField', [], {})
        },
        u'web.topcouponsection': {
            'Meta': {'ordering': "['order']", 'object_name': 'TopCouponSection'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'order': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['tracking']