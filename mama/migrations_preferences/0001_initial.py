# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Preferences'
        db.create_table('preferences_preferences', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('preferences', ['Preferences'])

        # Adding M2M table for field sites on 'Preferences'
        db.create_table('preferences_preferences_sites', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('preferences', models.ForeignKey(orm['preferences.preferences'], null=False)),
            ('site', models.ForeignKey(orm['sites.site'], null=False))
        ))
        db.create_unique('preferences_preferences_sites', ['preferences_id', 'site_id'])

        # Adding model 'SitePreferences'
        db.create_table('preferences_sitepreferences', (
            ('preferences_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['preferences.Preferences'], unique=True, primary_key=True)),
            ('pregnancy_helpline_number', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('baby_helpline_number', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('hivaids_helpline_number', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('about', self.gf('ckeditor.fields.RichTextField')(null=True, blank=True)),
            ('terms', self.gf('ckeditor.fields.RichTextField')(null=True, blank=True)),
        ))
        db.send_create_signal('preferences', ['SitePreferences'])


    def backwards(self, orm):
        # Deleting model 'Preferences'
        db.delete_table('preferences_preferences')

        # Removing M2M table for field sites on 'Preferences'
        db.delete_table('preferences_preferences_sites')

        # Deleting model 'SitePreferences'
        db.delete_table('preferences_sitepreferences')


    models = {
        'preferences.preferences': {
            'Meta': {'object_name': 'Preferences'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['sites.Site']", 'null': 'True', 'blank': 'True'})
        },
        'preferences.sitepreferences': {
            'Meta': {'object_name': 'SitePreferences', '_ormbases': ['preferences.Preferences']},
            'about': ('ckeditor.fields.RichTextField', [], {'null': 'True', 'blank': 'True'}),
            'baby_helpline_number': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'hivaids_helpline_number': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'preferences_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['preferences.Preferences']", 'unique': 'True', 'primary_key': 'True'}),
            'pregnancy_helpline_number': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'terms': ('ckeditor.fields.RichTextField', [], {'null': 'True', 'blank': 'True'})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['preferences']