# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Country'
        db.create_table('web_country', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
        ))
        db.send_create_signal('web', ['Country'])

        # Adding field 'Coupon.lastupdated'
        db.add_column('web_coupon', 'lastupdated',
                      self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Coupon.created'
        db.add_column('web_coupon', 'created',
                      self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Coupon.price'
        db.add_column('web_coupon', 'price',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)

        # Adding field 'Coupon.listprice'
        db.add_column('web_coupon', 'listprice',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)

        # Adding field 'Coupon.discount'
        db.add_column('web_coupon', 'discount',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)

        # Adding field 'Coupon.percent'
        db.add_column('web_coupon', 'percent',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding M2M table for field countries on 'Coupon'
        db.create_table('web_coupon_countries', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('coupon', models.ForeignKey(orm['web.coupon'], null=False)),
            ('country', models.ForeignKey(orm['web.country'], null=False))
        ))
        db.create_unique('web_coupon_countries', ['coupon_id', 'country_id'])


    def backwards(self, orm):
        # Deleting model 'Country'
        db.delete_table('web_country')

        # Deleting field 'Coupon.lastupdated'
        db.delete_column('web_coupon', 'lastupdated')

        # Deleting field 'Coupon.created'
        db.delete_column('web_coupon', 'created')

        # Deleting field 'Coupon.price'
        db.delete_column('web_coupon', 'price')

        # Deleting field 'Coupon.listprice'
        db.delete_column('web_coupon', 'listprice')

        # Deleting field 'Coupon.discount'
        db.delete_column('web_coupon', 'discount')

        # Deleting field 'Coupon.percent'
        db.delete_column('web_coupon', 'percent')

        # Removing M2M table for field countries on 'Coupon'
        db.delete_table('web_coupon_countries')


    models = {
        'web.category': {
            'Meta': {'object_name': 'Category'},
            'code': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'web.country': {
            'Meta': {'object_name': 'Country'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'})
        },
        'web.coupon': {
            'Meta': {'object_name': 'Coupon'},
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['web.Category']", 'symmetrical': 'False'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'countries': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['web.Country']", 'symmetrical': 'False'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'dealtypes': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['web.DealType']", 'symmetrical': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'directlink': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'discount': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastupdated': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'link': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'listprice': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'merchant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['web.Merchant']"}),
            'percent': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'price': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'ref_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'restriction': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'skimlinks': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'start': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'web.couponnetwork': {
            'Meta': {'object_name': 'CouponNetwork'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'})
        },
        'web.dealtype': {
            'Meta': {'object_name': 'DealType'},
            'code': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'web.merchant': {
            'Meta': {'object_name': 'Merchant'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'ref_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'})
        }
    }

    complete_apps = ['web']