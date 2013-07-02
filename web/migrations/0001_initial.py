# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Category'
        db.create_table('web_category', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=255, null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=255, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal('web', ['Category'])

        # Adding model 'DealType'
        db.create_table('web_dealtype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=255, null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=255, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal('web', ['DealType'])

        # Adding model 'Merchant'
        db.create_table('web_merchant', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ref_id', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
        ))
        db.send_create_signal('web', ['Merchant'])

        # Adding model 'CouponNetwork'
        db.create_table('web_couponnetwork', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
        ))
        db.send_create_signal('web', ['CouponNetwork'])

        # Adding model 'Coupon'
        db.create_table('web_coupon', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ref_id', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('merchant', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['web.Merchant'])),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('restriction', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('start', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('end', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('link', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('directlink', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('skimlinks', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal('web', ['Coupon'])

        # Adding M2M table for field categories on 'Coupon'
        db.create_table('web_coupon_categories', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('coupon', models.ForeignKey(orm['web.coupon'], null=False)),
            ('category', models.ForeignKey(orm['web.category'], null=False))
        ))
        db.create_unique('web_coupon_categories', ['coupon_id', 'category_id'])

        # Adding M2M table for field dealtypes on 'Coupon'
        db.create_table('web_coupon_dealtypes', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('coupon', models.ForeignKey(orm['web.coupon'], null=False)),
            ('dealtype', models.ForeignKey(orm['web.dealtype'], null=False))
        ))
        db.create_unique('web_coupon_dealtypes', ['coupon_id', 'dealtype_id'])


    def backwards(self, orm):
        # Deleting model 'Category'
        db.delete_table('web_category')

        # Deleting model 'DealType'
        db.delete_table('web_dealtype')

        # Deleting model 'Merchant'
        db.delete_table('web_merchant')

        # Deleting model 'CouponNetwork'
        db.delete_table('web_couponnetwork')

        # Deleting model 'Coupon'
        db.delete_table('web_coupon')

        # Removing M2M table for field categories on 'Coupon'
        db.delete_table('web_coupon_categories')

        # Removing M2M table for field dealtypes on 'Coupon'
        db.delete_table('web_coupon_dealtypes')


    models = {
        'web.category': {
            'Meta': {'object_name': 'Category'},
            'code': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'web.coupon': {
            'Meta': {'object_name': 'Coupon'},
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['web.Category']", 'symmetrical': 'False'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'dealtypes': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['web.DealType']", 'symmetrical': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'directlink': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'merchant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['web.Merchant']"}),
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