# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'PopularCoupon'
        db.delete_table(u'web_popularcoupon')

        # Deleting model 'FeaturedCoupon'
        db.delete_table(u'web_featuredcoupon')

        # Deleting model 'NewCoupon'
        db.delete_table(u'web_newcoupon')

        # Adding model 'TopCouponSection'
        db.create_table(u'web_topcouponsection', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'web', ['TopCouponSection'])

        # Adding model 'CategorySection'
        db.create_table(u'web_categorysection', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'web', ['CategorySection'])


    def backwards(self, orm):
        # Adding model 'PopularCoupon'
        db.create_table(u'web_popularcoupon', (
            ('coupon', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Coupon'])),
            ('date_added', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 8, 7, 0, 0), auto_now_add=True, blank=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('last_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'web', ['PopularCoupon'])

        # Adding model 'FeaturedCoupon'
        db.create_table(u'web_featuredcoupon', (
            ('coupon', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Coupon'])),
            ('date_added', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 8, 7, 0, 0), auto_now_add=True, blank=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('last_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'web', ['FeaturedCoupon'])

        # Adding model 'NewCoupon'
        db.create_table(u'web_newcoupon', (
            ('coupon', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Coupon'])),
            ('date_added', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 8, 7, 0, 0), auto_now_add=True, blank=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('last_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'web', ['NewCoupon'])

        # Deleting model 'TopCouponSection'
        db.delete_table(u'web_topcouponsection')

        # Deleting model 'CategorySection'
        db.delete_table(u'web_categorysection')


    models = {
        u'web.categorysection': {
            'Meta': {'ordering': "['order']", 'object_name': 'CategorySection'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'order': ('django.db.models.fields.IntegerField', [], {})
        },
        u'web.shortenedurlcomponent': {
            'Meta': {'object_name': 'ShortenedURLComponent'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'original_url': ('django.db.models.fields.TextField', [], {}),
            'shortened_url': ('django.db.models.fields.CharField', [], {'max_length': '35', 'db_index': 'True'})
        },
        u'web.topcouponsection': {
            'Meta': {'ordering': "['order']", 'object_name': 'TopCouponSection'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'order': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['web']